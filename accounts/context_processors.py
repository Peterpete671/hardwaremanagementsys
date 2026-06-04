def user_permissions(request):
    is_admin_user = False
    if request.user.is_authenticated:
        is_admin_user = request.user.user_roles.filter(
            role__name='ADMIN',
            is_active=True
        ).exists() or request.user.is_superuser
    return {
        'is_admin_user': is_admin_user,
    }
