def menu_state(request):
    menu_fold = request.COOKIES.get("menu_fold") == "1"
    return {
        "is_menu_folded": menu_fold
    }