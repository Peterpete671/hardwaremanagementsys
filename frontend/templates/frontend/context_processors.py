def admin_status(request):
    """Makes is_admin available in every template automatically."""
    is_admin = False
    if request.user.is_authenticated:
        is_admin = request.user.is_superuser or request.user.user_roles.filter(
            role__name='ADMIN', is_active=True
        ).exists()
    return {'is_admin': is_admin}