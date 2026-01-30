from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from novels.models import Novel

@login_required
def dashboard_view(request):
    """
    Dashboard showing the user's novels.
    """
    novels = Novel.objects.filter(user=request.user, archived=False)
    if not novels.exists():
        return render(request, 'core/dashboard.html', {'novels': novels})
    return redirect('novel_list')
