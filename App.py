import flet as ft
import Pages as pg
import os
from Account import sign_out

def main(page: ft.Page):
    page.title = "Ledger Logic"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1400
    page.window_height = 1000
    page.window_center()
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Content area to display the selected page
    content_area = ft.Container(expand=True)

    # Function to load the page content based on selected section
    def load_page_content(content):
        content_area.content = content
        page.update()

    def logout(event):  # Accept the event parameter
        sign_out()
        page.clean()
        page.add(ft.Row(controls=[content_area], expand=True))
        show_login()

    sign_out_button = ft.ElevatedButton(
        "Sign Out",
        icon=ft.icons.LOGOUT,
        style=ft.ButtonStyle(
            color=ft.colors.RED_400,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        on_click=logout
    )

    def create_nav_button(icon, label, route):
        return ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(icon),
                ft.Text(label)
            ]),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            data=route,  # Store the route in the button's data attribute
            on_click=lambda _: navigate_to_page(route)
        )

    nav_buttons = [
        create_nav_button(ft.icons.HOME_OUTLINED, "Home", "home"),
        create_nav_button(ft.icons.BOOK_OUTLINED, "Journal", "journal"),
        create_nav_button(ft.icons.ACCOUNT_BALANCE_OUTLINED, "Ledger", "ledger"),
        create_nav_button(ft.icons.BALANCE_OUTLINED, "Trial Balance", "trial-balance"),
        create_nav_button(ft.icons.CHAT_OUTLINED, "Chatbot", "chatbot"),
        create_nav_button(ft.icons.SETTINGS_OUTLINED, "Settings", "settings")
    ]

    side_bar = ft.Column(
        controls=[
            *nav_buttons,
            ft.Container(height=20),  # Spacer
            sign_out_button
        ],
        width=200,
        alignment=ft.MainAxisAlignment.START,
        spacing=10
    )

    def on_route_change(e):
        route = page.route.lstrip("/")
        navigate_to_page(route)
    
    # Set the route change handler
    page.on_route_change = on_route_change
    def navigate_to_page(route):
    
        if route == "home":
            load_page_content(pg.home_page(page))
        elif route == "journal":
            load_page_content(pg.journal_page(page))
        elif route == "ledger":
            load_page_content(pg.ledger_page(page))
        elif route == "trial-balance":
            load_page_content(pg.trial_balance_page(page))
        elif route == "chatbot":
            load_page_content(pg.chatbot_page(page))
        elif route == "settings":
            load_page_content(pg.settings_page(page))
        elif route == "edit_profile":
            load_page_content(pg.edit_profile_page(page))
        elif route == "change_password":
            load_page_content(pg.change_password_page(page))
        elif route == "delete_account":
            load_page_content(pg.delete_account_page(page))
            
    def signed_in():
        page.add(
            ft.Row(
                controls=[side_bar, content_area],
                expand=True  # Makes Row take up full width and height of the page
            )
        )

    def show_login():
        page.clean()
        pg.login_page(page, on_login_success=lambda: [pg.splash_screen(page), signed_in(), load_page_content(pg.home_page(page))])

    pg.splash_screen(page)
    show_login()


if __name__ == "__main__":
    ft.app(main, assets_dir="Images")

try:
    os.remove("Log\\Signed_In.txt")
except:
    pass
