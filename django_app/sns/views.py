from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import Message, Friend, Group, Good
from .forms import GroupCheckForm, GroupSelectForm, FriendsForm, CreateGroupForm, PostForm

@login_required(login_url='/admin/login/')
def index(request, page=1):
    (public_user, public_group) = get_public()

    if request.method == 'POST':
        checkform = GroupCheckForm(request.user, request.POST)
        glist = []
        for item in request.POST.getlist('groups'):
            glist.append(item)
        messages = get_your_group_message(request.user, glist, page)
    else:
        checkform = GroupCheckForm(request.user)
        gps = Group.objects.filter(owner=request.user)
        glist = [public_group.title]
        for item in gps:
            glist.append(item.title)
        messages = get_your_group_message(request.user, glist, page)
    params = {
        'login_user':request.user,
        'contents':messages,
        'check_form':checkform
    }
    return render(request, 'sns/index.html', params)

@login_required(login_url='/admin/login/')
def groups(request):
    friends = Friend.objects.filter(owner=request.user)
    
    if request.method == 'POST':
        if request.POST['mode'] == '__groups_form__':
            sel_group = request.POST.get('groups')
            gp = Group.objects.filter(owner=request.user).filter(title=sel_group).first()
            fds = Friend.objects.filter(owner=request.user).filter(group=gp)
            print(Friend.objects.filter(owner=request.user))
            vlist = []
            for item in fds:
                vlist.append(item.user.username)
            groupsform = GroupSelectForm(request.user, request.POST)
            friendsform = FriendsForm(request.user, friends=friends, vals=vlist)

        if request.POST['mode'] == '__friends_form__':
            sel_group = request.POST['group']
            group_obj = Group.objects.filter(title=sel_group).first()
            print(group_obj)
            sel_fds = request.POST.getlist('friends')
            sel_users = User.objects.filter(username__in=sel_fds)
            fds = Friend.objects.filter(owner=request.user).filter(user__in=sel_users)
            vlist = []
            for item in fds:
                item.group = group_obj
                item.save()
                vlist.append(item.user.username)
            messages.success(request, ' チェックされたFriendを ' + sel_group + 'に登録しました。')
            groupsform = GroupSelectForm(request.user, {'groups':sel_group})
            friendsform = FriendsForm(request.user, friends=friends, vals=vlist)

    else:
        groupsform = GroupSelectForm(request.user)
        friendsform = FriendsForm(request.user, friends=friends, vals=[])
        sel_group = '-'
    
    createform = CreateGroupForm()
    params = {
        'login_user':request.user,
        'gropus_form':groupsform,
        'friends_form':friendsform,
        'create_form':createform,
        'group':sel_group,
    }
    return render(request, 'sns/groups.html', params)

@login_required(login_url='/admin/login/')
def add(request):
    add_name = request.GET['name']
    add_user = User.objects.filter(username=add_name).first()
    if add_user == request.user:
        messages.info(request, "自分自身をFriendに追加することはできません。")
        return redirect(to='/sns')
    (public_user, public_group) = get_public()
    frd_num = Friend.objects.filter(owner=request.user).filter(user=add_user).count()
    if frd_num > 0:
        messages.info(request, add_user.username + ' は既に追加されています。')
        return redirect(to='/sns')

    frd = Friend()
    frd.owner = request.user
    frd.user = add_user
    frd.group = public_group
    frd.save()

    messages.success(request, add_user.username + ' を追加しました！ groupページに移動して、追加したFriendをメンバーに設定してください。')
    return redirect(to='/sns')

@login_required(login_url='/admin/login/')
def creategroup(request):
    gp = Group()
    gp.owner = request.user
    gp.title = request.user.username + ' の' + request.POST['group_name']
    gp.save()
    messages.info(request, '新しいグループを作成しました。')
    return redirect(to='/sns/groups')

@login_required(login_url='/admin/login/')
def post(request):
    if request.method == 'POST':
        gr_name = request.POST['groups']
        content = request.POST['content']
        group = Group.objects.filter(owner=request.user).filter(title=gr_name).first()
        
        if group == None:
            (pub_user, group) = get_public()
        msg = Message()
        msg.owner = request.user
        msg.group = group
        msg.content = content
        msg.save()

        messages.success(request, '新しいメッセージを投稿しました！ ')
        return redirect(to='/sns')
    
    else:
        form = PostForm(request.user)

    params = {
        'login_user':request.user,
        'form':form
    }

    return render(request, 'sns/post.html', params)

@login_required(login_url='/admin/login/')
def share(request, share_id):
    share = Message.objects.get(id=share_id)
    print(share)

    if request.method == 'POST':
        gr_name = request.POST['groups']
        content = request.POST['content']

        group = Group.objects.filter(owner=request.user).filter(title=gr_name).first()
        if group == None:
            (pub_user, group) = get_public()
        msg = Message()
        msg.owner = request.user
        msg.group = group
        msg.content = content
        msg.share_id = share.id
        msg.save()
        share_msg = msg.get_share()
        share_msg.share_count += 1
        share_msg.save()

        messages.success(request, 'メッセージをシェアしました！ ')
        return redirect(to='/sns')
    
    form = PostForm(request.user)
    params = {
        'login_user':request.user,
        'form':form,
        'share':share,
    }
    return render(request, 'sns/share.html', params)

@login_required(login_url='/admin/login/')
def good(request, good_id):
    good_msg = Message.objects.get(id=good_id)
    is_good = Good.objects.filter(owner=request.user).filter(message=good_msg).count()
    if is_good > 0:
        messages.success(request, '既にメッセージにはGoodしています。')
        return redirect(to='/sns')

    good_msg.good_count += 1
    good_msg.save()
    good = Good()
    good.owner = request.user
    good.message = good_msg
    good.save()

    messages.success(request, 'メッセージにGoodしました！')
    return redirect(to='/sns')


def get_your_group_message(owner, glist, page):
    page_num = 10
    (public_user, public_group) = get_public()
    groups = Group.objects.filter(Q(owner=owner)|Q(owner=public_user)).filter(title__in=glist)
    me_friends = Friend.objects.filter(group__in=groups)
    me_users = []
    for f in me_friends:
        me_users.append(f.user)
    his_groups = Group.objects.filter(owner__in=me_users)
    his_friends = Friend.objects.filter(user=owner).filter(group__in=his_groups)
    me_groups = []
    for hf in his_friends:
        me_groups.append(hf.group)
    messages = Message.objects.filter(Q(group__in=groups)|Q(group__in=me_groups))
    page_item = Paginator(messages, page_num)
    return page_item.get_page(page)

def get_public():
    public_user = User.objects.filter(username='public').first()
    public_group = Group.objects.filter(owner=public_user).first()
    return (public_user, public_group)
