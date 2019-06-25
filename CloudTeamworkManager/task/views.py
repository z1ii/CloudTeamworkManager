from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission, Group
from guardian.shortcuts import assign_perm, remove_perm
from guardian.decorators import permission_required_or_403
from .models import task as models_task
from .models import comment as models_comment
from .forms import task as forms_task
from .forms import comment as forms_comment
from account.models import UserProfile
import re
import json


# 请注意，这个函数不会修改target_user的权限
def remove_user(target_user, target_task):
    target_user.involved_projects_number -= 1
    target_user.involved_projects = json.dumps(json.loads(target_user.involved_projects).remove(target_task.id))
    target_user.save()

def add_user(target_user, target_group, target_task, position = 0):
    target_user.involved_projects_number += 1
    target_user.involved_projects = json.dumps(json.loads(user.involved_projects).append(target_task.id))
    target_user.save()

    user = User.objects.get(id = target_user.user_id)
    user.groups.add(target_group)

@permission_required_or_403("task.create_tasks")
def create_task(request):
    if request.method == "GET":
        return render(request, "create_task.html", {"form": forms_task()})

    if request.method == "POST":
        form = forms_task(request.POST)

        if form.is_valid():
            form.instance.all_members = json.dumps(json.loads(form.instance.members).append(request.user.id))
            form.instance.creator = request.user.id

            target_task = form.save()

            # 配置组权限
            group = Group.objects.create(name=str(target_task.id))
            assign_perm('glance_over_task_details', group, target_task)

            # 配置创建者权限
            assign_perm('edit_tasks', request.user, target_task)
            assign_perm('view_comments', request.user, target_task)
            
            # 配置组长权限
            for each in json.loads(request.POST.get("leaders")):
                try:
                    target_user = UserProfile.objects.get(id = each)
                except UserProfile.DoesNotExist:
                    continue

                assign_perm('edit_comments', target_user, target_task)
                assign_perm('view_comments', target_user, target_task)

            # 配置组员权限
            for each in json.loads(form.instance.members):
                try:
                    target_user = UserProfile.objects.get(id = each)
                except UserProfile.DoesNotExist:
                    continue

                add_user(target_user, group, target_task)

            # 通知

            return HttpResponse("200")
        return HttpResponse("出现错误")

@permission_required_or_403("task.edit_tasks", (models_task, "id", "task_id"))
def edit_task(request, task_id):
    if request.method == 'GET':
        target_task = models_task.objects.get(id = task_id)
        return render(request, "create_task.html", {"form": forms_task(instance = target_task)})

    if request.method == "POST":
        target_task = models_task.objects.get(id = task_id)
        form = forms_task(request.POST, instance = target_task)

        if form.is_valid():
            # 计算新增成员和被移除的成员
            past_members = set(json.loads(target_task.members))
            current_members = set(json.loads(request.POST.get("members")))
            removed_members = past_members - current_members
            new_members = current_members - past_members

            # 更新参与过该任务的成员列表
            form.instance.all_members = json.dumps(list(set(json.loads(form.instance.all_members)) + current_members))
            form.save()

            # 获取权限组
            group = Group.objects.get(name=str(target_task.id))

            # 在组中删除该成员，该成员参与过的任务列表更新
            for i in removed_members:
                try:
                    user = UserProfile.objects.get(id = i)
                except UserProfile.DoesNotExist:
                    continue

                remove_user(user, group, target_task)
                User.objects.get(id = user.user_id).groups.remove(group)

                # 通知

            # 计算新增组长和被移除的组长
            past_leaders = set(json.loads(target_task.leaders))
            current_leaders = set(json.loads(request.POST.get("members")))
            removed_leaders = past_leaders - current_leaders
            new_leaders = current_leaders - past_leaders

            # 配置被移除的组长的权限
            for i in removed_leaders:
                try:
                    user = UserProfile.objects.get(id = i)
                except UserProfile.DoesNotExist:
                    continue

                remove_perm('view_comments', User.objects.get(id = user.user_id), target_task)
                remove_perm('edit_comments', User.objects.get(id = user.user_id), target_task)

                # 通知

            # 配置新增组员
            for i in new_members:
                try:
                    user = UserProfile.objects.get(id = i)
                except UserProfile.DoesNotExist:
                    continue

                add_user(user, target_task)

                # 通知

            # 配置新增组长的权限
            for i in new_leaders:
                try:
                    user = UserProfile.objects.get(id = i)
                except UserProfile.DoesNotExist:
                    continue

                add_perm('view_comments', User.objects.get(id = user.user_id), target_task)
                add_perm('edit_comments', User.objects.get(id = user.user_id), target_task)

                # 通知

            return HttpResponse("200")
        return HttpResponse("出现错误")

@permission_required_or_403("task.edit_tasks", (models_task, "id", "task_id"))
def delete_task(request, task_id):
    target_task = models_task.objects.get(id = task_id)
    members = json.loads(target_task.members)
    
    # 撤销权限
    Group.objects.get(name=str(target_task.id)).delete()
    remove_perm('edit_tasks', request.user, target_task)
    remove_perm('view_comments', request.user, target_task)

    for each in json.loads(target_task.leaders):
        target_user = User.objects.get(id = each)
        remove_perm('view_comments', target_user, target_task)
        remove_perm('edit_comments', target_user, target_task)

    # 组内成员参与任务的个数减一，删除参与该任务的记录
    for each in members:
        try:
            user = UserProfile.objects.get(id = each)
        except UserProfile.DoesNotExist:
            continue
        
        remove_user(user, target_task)

    # 通知

    return HttpResponse("200")

@permission_required_or_403("task.create_tasks")
def get_members(request):
    members = UserProfile.objects.filter(magor=request.GET.get("key")) | UserProfile.objects.filter(name = request.GET.get("key"))
    members = members.values("name", "magor", "user_id", "involved_projects_number")
    return HttpResponse(json.dumps(list(members)))

@permission_required_or_403("task.glance_over_task_details", (models_task, "id", "task_id"))
def task_page(request, task_id):
    target_task = models_task.objects.get(id = task_id)
    return HttpResponse(target_task)

def process(request, task_id):
    target_task = models_task.objects.get(id = task_id)
    # 更新项目进度,修改项目进度
    if request.method == "GET":
        if request.user.has_perm("comment.view_comments", target_task):
            progress = target_task.task_progress
            return HttpResponse(progress)
        return HttpResponse(status=403)

    if request.method == "POST":
        if request.user.has_perm("comment.edit_comments", target_task):
            if request.POST.get("action") == "upgrade":
                target_task.task_progress = "%s|%s"%(target_task.task_progress, request.POST.get("task_progress"))
                target_task = forms_task(target_task)
            elif request.POST.get("action") == "edit":
                target_task.task_progress = "%s%s"%(re.match("^.*\|", target_task.task_progress).group(), request.POST.get("task_progress"))
                target_task = forms_task(target_task)
            if target_task.is_valid():
                target_task.save()
                return HttpResponse('200')
            return HttpResponse('出现了一些错误!')
        return HttpResponse(status=403)

#@permission_required_or_403("comment.edit_comments")
#def comment(request):
#    if request.method == "GET":
#        return HttpResponse(json.dumps(list(models_comment.objects.get(id = request.GET.get("comment_id")).values("content"))))

#    if request.method == "POST":
#        if request.POST.get("action") == "upgrade":
#            target_comment = models_task.objects.get(id = request.POST.get("comment_id"))
#            if not target_comment.previous:
#                target_comment.content = request.POST.get("content")
#                target_comment = forms_comment(target_comment)
#                if target_comment.is_valid():
#                    target_comment.save()
#                    return HttpResponse('200')
#                return HttpResponse('出现了一些错误!')
#            return HttpResponse('不允许修改以往的评价!')
#        elif request.POST.get("action") == "create":
#            target_comment = forms_comment(request.POST.get("content"))
#            target_comment.instance.creator = UserProfile.objects.get(user_id = request.user.id)
#            target_comment.instance.user_id = request.POST.get("user_id")            target_task.task_progress = "%s%s"%(re.match("^.*\|", target_task.task_progress).group(), request.POST.get("task_progress"))
#            target_task = forms_task(target_task)
#            if target_task.is_valid():
#                target_task.save()
#                return HttpResponse('200')
#            return HttpResponse('出现了一些错误!')