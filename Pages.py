import flet as ft
import datetime as dt
import time
import threading
from PIL import Image
import tempfile
import os
import io
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

import Account
from Export import export_journal_xlsx, export_ledger_xlsx, export_tb_xlsx, export_all_xlsx
from Journal import add_journal, all_journals, edit_journal, dele_journal, assets_liabilities
from Ledger import get_ledger_format
from Trial_Balance import get_trial_balance
from Chatbot import ask, get_history

def show_banner(page: ft.Page, message: str, color: str = ft.colors.BLUE, folder_path: str = None):
    def close_banner():
        page.banner.open = False
        page.update()

    def open_folder(e):
        if folder_path:
            os.startfile(os.path.dirname(folder_path))

    # Create action buttons for the banner
    actions = [ft.TextButton("DISMISS", on_click=lambda e: close_banner())]
    if folder_path:
        actions.insert(0, ft.TextButton("Open Folder", on_click=open_folder))

    banner = ft.Banner(
        bgcolor=color,
        content=ft.Text(message, color=ft.colors.WHITE),
        leading=ft.Icon(ft.icons.INFO, color=ft.colors.WHITE),
        actions=actions
    )
    page.banner = banner
    page.banner.open = True
    page.update()

    # Run `close_banner` without parameters after 5 seconds
    threading.Timer(5, close_banner).start()

def splash_screen(page: ft.Page):
    progress_ring = ft.ProgressRing()
    
    splash_content = ft.Column(
        [   
            ft.Image(
                src="Images\\Logo.png",
                width=200,
                height=200,
                fit=ft.ImageFit.CONTAIN
            ),
            ft.Text("Welcome to Ledger Logic", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Loading...", size=16),
            progress_ring
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(
        ft.Container(
            content=splash_content,
            alignment=ft.alignment.center,
            expand=True
        )
    )

    time.sleep(3)
    page.clean()

def login_page(page: ft.Page, on_login_success):
    def switch_to_signup():
        page.clean()
        signup_page(page, on_login_success)
        
    def switch_to_reset():
        page.clean()
        reset_password_page(page, on_login_success)
    
    def login(e):
        if not username.value or not password.value:
            show_banner(page, "Please fill in all fields", ft.colors.RED)
            return
            
        if Account.sign_in(username.value, password.value):
            username.value = ""
            password.value = ""
            page.clean()
            on_login_success()
        else:
            show_banner(page, "Invalid credentials", ft.colors.RED)

    page.title = "Login - Ledger Logic"
    
    # Create the logo image
    logo = ft.Image(
        src="Images/Logo.png",
        width=200,
        height=200,
        fit=ft.ImageFit.CONTAIN
    )
    
    # Create input fields
    username = ft.TextField(
        label="Username",
        autofocus=True,
        prefix_icon=ft.icons.PERSON,
        width=300
    )
    
    password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK,
        width=300
    )

    # Create buttons
    login_button = ft.ElevatedButton(
        text="Login",
        width=300,
        on_click=login,
        style=ft.ButtonStyle(
            color={
                ft.MaterialState.HOVERED: ft.colors.WHITE,
                ft.MaterialState.FOCUSED: ft.colors.WHITE,
                ft.MaterialState.DEFAULT: ft.colors.BLACK,
            },
            bgcolor={
                ft.MaterialState.FOCUSED: ft.colors.BLUE, 
                ft.MaterialState.HOVERED: ft.colors.BLUE,
                ft.MaterialState.DEFAULT: ft.colors.BLUE_200,
            },
        )
    )

    signup_button = ft.TextButton(
        text="Don't have an account? Sign up",
        on_click=lambda _: switch_to_signup()
    )

    forgot_password = ft.TextButton(
        text="Forgot Password?",
        on_click=lambda _: switch_to_reset()
    )

    # Create the main content layout
    login_content = ft.Column(
        [
            logo,
            ft.Text("Welcome Back!", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Please login to your account", size=16, color=ft.colors.GREY),
            username,
            password,
            login_button,
            forgot_password,
            signup_button,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

    page.add(
        ft.Container(
            content=login_content,
            alignment=ft.alignment.center,
            expand=True,
            padding=50,
        )
    )
    page.update()

def signup_page(page: ft.Page, on_login_success):
    def switch_to_login():
        page.clean()
        login_page(page, on_login_success)
    
    def validate_date(date_str):
        try:
            dt.datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def handle_file_picker_result(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            # Read the image file
            file_path = e.files[0].path
            with Image.open(file_path) as img:
                # Resize image to a reasonable size
                img.thumbnail((256, 256))
                # Convert to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
                profile_picture_data = img_byte_arr.getvalue()
                return profile_picture_data
        return None

    def signup(e):
        if not all([username.value, password.value, confirm_password.value, 
                   email.value, phone.value]):
            show_banner(page, "Please fill in all required fields", ft.colors.RED)
            return
        
        if password.value != confirm_password.value:
            show_banner(page, "Passwords do not match", ft.colors.RED)
            return
        
        # Get the selected date from the CupertinoDatePicker
        selected_date = dob.value.strftime('%Y-%m-%d')
        
        profile_picture = None
        if file_picker.result and file_picker.result.files:
            profile_picture = handle_file_picker_result(file_picker.result)
        
        success, message = Account.sign_up(
            username.value,
            password.value,
            email.value,
            selected_date,
            phone.value,
            profile_picture,
            bio.value
        )
        
        if success:
            show_banner(page, f"Account created successfully! Your recovery key is: {message}", ft.colors.GREEN)
            switch_to_login()
        else:
            show_banner(page, f"Failed to create account: {message}", ft.colors.RED)

    page.title = "Sign Up - Ledger Logic"
    
    # Create file picker
    file_picker = ft.FilePicker(
        on_result=handle_file_picker_result
    )
    page.overlay.append(file_picker)
    
    # Create input fields
    username = ft.TextField(label="Username", prefix_icon=ft.icons.PERSON, width=300)
    password = ft.TextField(label="Password", password=True, prefix_icon=ft.icons.LOCK, width=300)
    confirm_password = ft.TextField(label="Confirm Password", password=True, prefix_icon=ft.icons.LOCK, width=300)
    email = ft.TextField(label="Email", prefix_icon=ft.icons.EMAIL, width=300)
    phone = ft.TextField(label="Phone Number", prefix_icon=ft.icons.PHONE, width=300)
    dob = ft.CupertinoDatePicker(
        width=300, height=100,
        date_picker_mode=ft.CupertinoDatePickerMode.DATE,
        date_order = ft.CupertinoDatePickerDateOrder.DAY_MONTH_YEAR,
    )    
    bio = ft.TextField(label="Biography", multiline=True, width=300)
    
    # Create buttons
    signup_button = ft.ElevatedButton(
        text="Sign Up",
        width=300,
        on_click=signup,
        style=ft.ButtonStyle(
            color={
                ft.MaterialState.HOVERED: ft.colors.WHITE,
                ft.MaterialState.FOCUSED: ft.colors.WHITE,
                ft.MaterialState.DEFAULT: ft.colors.BLACK,
            },
            bgcolor={
                ft.MaterialState.FOCUSED: ft.colors.BLUE, 
                ft.MaterialState.HOVERED: ft.colors.BLUE,
                ft.MaterialState.DEFAULT: ft.colors.BLUE_200,
            },
        )
    )
    
    profile_pic_button = ft.ElevatedButton(
        "Upload Profile Picture",
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=['png', 'jpg', 'jpeg']
        )
    )

    login_button = ft.TextButton(
        text="Already have an account? Login",
        on_click=lambda _: switch_to_login()
    )

    # Create the main content layout using ListView
    signup_content = ft.ListView(
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Create Account", size=32, weight=ft.FontWeight.BOLD),
                        ft.Text("Please fill in the details below", size=16, color=ft.colors.GREY),
                        username,
                        password,
                        confirm_password,
                        email,
                        phone,
                        ft.Text("Date of Birth", size=16),  # Add a label for the date picker
                        dob,
                        bio,
                        profile_pic_button,
                        signup_button,
                        login_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                padding=ft.padding.all(50),
                alignment=ft.alignment.center,
            )
        ],
        expand=True,
        spacing=10,
        padding=10,
        auto_scroll=True
    )

    # Add everything to the page
    page.add(signup_content)
    page.update()

def reset_password_page(page: ft.Page, on_login_success):
    def switch_to_login():
        page.clean()
        login_page(page, on_login_success)
    
    def reset_password(e):
        if not all([username.value, recovery_key.value, new_password.value, 
                   confirm_password.value]):
            show_banner(page, "Please fill in all fields", ft.colors.RED)
            return
            
        if new_password.value != confirm_password.value:
            show_banner(page, "Passwords do not match", ft.colors.RED)
            return
            
        if Account.reset_pas(username.value, recovery_key.value, new_password.value):
            show_banner(page, "Password reset successful!", ft.colors.GREEN)
            switch_to_login()
        else:
            show_banner(page, "Invalid username or recovery key", ft.colors.RED)

    page.title = "Reset Password - Ledger Logic"
    
    # Create input fields
    username = ft.TextField(label="Username", prefix_icon=ft.icons.PERSON, width=300)
    recovery_key = ft.TextField(label="Recovery Key", prefix_icon=ft.icons.KEY, width=300)
    new_password = ft.TextField(label="New Password", password=True, prefix_icon=ft.icons.LOCK, width=300)
    confirm_password = ft.TextField(label="Confirm New Password", password=True, prefix_icon=ft.icons.LOCK, width=300)

    # Create buttons
    reset_button = ft.ElevatedButton(
        text="Reset Password",
        width=300,
        on_click=reset_password,
        style=ft.ButtonStyle(
            color={
                ft.MaterialState.HOVERED: ft.colors.WHITE,
                ft.MaterialState.FOCUSED: ft.colors.WHITE,
                ft.MaterialState.DEFAULT: ft.colors.BLACK,
            },
            bgcolor={
                ft.MaterialState.FOCUSED: ft.colors.BLUE, 
                ft.MaterialState.HOVERED: ft.colors.BLUE,
                ft.MaterialState.DEFAULT: ft.colors.BLUE_200,
            },
        )
    )

    back_to_login = ft.TextButton(
        text="Back to Login",
        on_click=lambda _: switch_to_login()
    )

    # Create the main content layout
    reset_content = ft.Column(
        [
            ft.Text("Reset Password", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Enter your details to reset your password", size=16, color=ft.colors.GREY),
            username,
            recovery_key,
            new_password,
            confirm_password,
            reset_button,
            back_to_login,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

    page.add(
        ft.Container(
            content=reset_content,
            alignment=ft.alignment.center,
            expand=True,
            padding=50,
        )
    )
    page.update()

def home_page(page: ft.Page):
    def create_pie_chart(data, title):
        labels = list(data.keys())
        sizes = list(data.values())
        colors = ['#1f77b4' if "Asset" in title else '#ff7f0e' for _ in labels]  # Different color per type
        explode = [0.05] * len(labels)  # Slightly separate each slice

        plt.figure(figsize=(6, 6))
        plt.pie(
            sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors,
            explode=explode, shadow=True, wedgeprops=dict(edgecolor='black', linewidth=1.2)
        )
        plt.title(title)

        # Save the chart to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(temp_file.name)
        plt.close()
        
        return temp_file.name

    def create_charts_container():
        assets, liabilities = assets_liabilities()
        assets_chart_path = create_pie_chart(assets, "Assets Distribution")
        liabilities_chart_path = create_pie_chart(liabilities, "Liabilities Distribution")

        assets_chart_image = ft.Image(src=assets_chart_path, width=500, height=500)
        liabilities_chart_image = ft.Image(src=liabilities_chart_path, width=500, height=500)

        # Place charts side by side
        return ft.Row([assets_chart_image, liabilities_chart_image], alignment=ft.MainAxisAlignment.CENTER)

    welcome_text = ft.Text("Welcome to Ledger Logic", size=32, weight=ft.FontWeight.BOLD)
    overview_text = ft.Text("Financial Overview", size=24, weight=ft.FontWeight.BOLD)
    chart_container = ft.Container(content=create_charts_container(), alignment=ft.alignment.center)

    # Combine the elements into the main content
    content = ft.Column(
        controls=[
            welcome_text,
            ft.Divider(),
            overview_text,
            chart_container,
            ft.Divider(),
        ],
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    return ft.Container(
        content=content,
        padding=20,
        expand=True,
        alignment=ft.alignment.top_center
    )

def journal_page(page: ft.Page):
    def add_journal_menu():
        input_fields = ft.Column([
            ft.TextField(label="Debit Account", hint_text="Enter debit account"),
            ft.TextField(label="Credit Account", hint_text="Enter credit account"),
            ft.TextField(label="Amount", hint_text="Enter amount", input_filter=ft.NumbersOnlyInputFilter()),
            ft.TextField(label="Narration", hint_text="Enter narration"),
        ])
        
        def close_add_dialog(e):
            add_dialog.open = False
            page.update()
        
        def handle_submit(e):
            debit = input_fields.controls[0].value.strip()
            credit = input_fields.controls[1].value.strip()
            amount = input_fields.controls[2].value
            narration = input_fields.controls[3].value.strip()
            
            if not all([debit, credit, amount, narration]):
                show_banner(page, "Please fill in all fields", ft.colors.RED)
                return
                
            try:
                amount = float(amount)
                add_journal(debit, credit, amount, narration)
                show_banner(page, "Journal entry added successfully!", ft.colors.GREEN)
                close_add_dialog(None)
                refresh_journal_table()
                page.update()
            except ValueError:
                show_banner(page, "Please enter a valid amount", ft.colors.RED)
        
        add_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Journal Entry"),
            content=input_fields,
            actions=[
                ft.TextButton("Cancel", on_click=close_add_dialog),
                ft.TextButton("Add", on_click=handle_submit),
            ],
        )
        
        return add_dialog

    def edit_journal_menu():
        journals = all_journals()
        if not journals:
            return ft.AlertDialog(
                modal=True,
                title=ft.Text("Edit Journal Entry"),
                content=ft.Text("No journal entries available to edit."),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: setattr(dlg_modal, 'open', False)),
                ],
            )
        
        selected_index = None
        journal_dropdown = ft.Dropdown(
            width=500,
            label="Select Journal Entry",
            options=[
                ft.dropdown.Option(
                    f"{j[0]}: {j[2]} to {j[3]} - {j[4]}"
                ) for j in journals
            ]
        )
        
        input_fields = ft.Column([
            journal_dropdown,
            ft.TextField(label="Debit Account", width=300),
            ft.TextField(label="Credit Account", width=300),
            ft.TextField(label="Amount", width=300, input_filter=ft.NumbersOnlyInputFilter()),
            ft.TextField(label="Narration", width=300),
        ])
        
        def handle_selection_change(e):
            nonlocal selected_index
            if journal_dropdown.value:
                selected_index = int(journal_dropdown.value.split(':')[0])
                journal = next(j for j in journals if j[0] == selected_index)
                input_fields.controls[1].value = journal[2]
                input_fields.controls[2].value = journal[3]
                input_fields.controls[3].value = str(journal[4])
                input_fields.controls[4].value = journal[5]
                page.update()
        
        journal_dropdown.on_change = handle_selection_change
        
        def handle_edit_submit(e):
            if not selected_index:
                show_banner(page, "Please select a journal entry", ft.colors.RED)
                return
                
            debit = input_fields.controls[1].value
            credit = input_fields.controls[2].value
            amount = input_fields.controls[3].value
            narration = input_fields.controls[4].value
            
            if not all([debit, credit, amount, narration]):
                show_banner(page, "Please fill in all fields", ft.colors.RED)
                return
                
            try:
                amount = float(amount)
                edit_journal(selected_index, debit, credit, amount, narration)
                show_banner(page, "Journal entry updated successfully!", ft.colors.GREEN)
                dlg_modal.open = False
                refresh_journal_table()
                page.update()
            except ValueError:
                show_banner(page, "Please enter a valid amount", ft.colors.RED)
        
        def close_edit_dialog(e):
            dlg_modal.open = False
            page.update()

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Journal Entry"),
            content=input_fields,
            actions=[
                ft.TextButton("Cancel", on_click=close_edit_dialog),
                ft.TextButton("Update", on_click=handle_edit_submit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        return dlg_modal

    def delete_journal_menu():
        journals = all_journals()
        if not journals:
            return ft.AlertDialog(
                modal=True,
                title=ft.Text("Delete Journal Entry"),
                content=ft.Text("No journal entries available to delete."),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: setattr(dlg_modal, 'open', False)),
                ],
            )
        
        journal_dropdown = ft.Dropdown(
            width=300,
            label="Select Journal Entry to Delete",
            options=[
                ft.dropdown.Option(
                    f"{j[0]}: {j[2]} to {j[3]} - {j[4]}"
                ) for j in journals
            ]
        )
        
        def handle_delete_submit(e):
            if not journal_dropdown.value:
                show_banner(page, "Please select a journal entry", ft.colors.RED)
                return
                
            selected_index = int(journal_dropdown.value.split(':')[0])
            dele_journal(selected_index)
            show_banner(page, "Journal entry deleted successfully!", ft.colors.GREEN)
            dlg_modal.open = False
            refresh_journal_table()
            page.update()
        
        def close_delete_dialog(e):
            dlg_modal.open = False
            page.update()

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Journal Entry"),
            content=ft.Column([
                journal_dropdown,
                ft.Text("Warning: This action cannot be undone.", color=ft.colors.RED),
            ]),
            actions=[
                ft.TextButton("Cancel", on_click=close_delete_dialog),
                ft.TextButton("Delete", on_click=handle_delete_submit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        return dlg_modal

    def create_journal_table():
        journals = all_journals()
        if not journals:
            return ft.Text("No journal entries available.")
        
        table_rows = []
        for journal in journals:
            # Create row for debit entry
            row_1 = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(journal[0]))),  # Index
                    ft.DataCell(ft.Text(journal[1])),       # Date
                    ft.DataCell(ft.Text(journal[2])),       # Debit account
                    ft.DataCell(ft.Text(f"{journal[4]:.2f}"))  # Amount
                ]
            )
            table_rows.append(row_1)
            
            # Create row for credit entry
            row_2 = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("")),  # Empty Index
                    ft.DataCell(ft.Text("")),  # Empty Date
                    ft.DataCell(ft.Text(f"        To {journal[3]}")),  # Credit account
                    ft.DataCell(ft.Text(f"{        journal[4]:.2f}"))  # Amount
                ]
            )
            table_rows.append(row_2)
            
            # Create row for narration
            row_3 = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("")),  # Empty Index
                    ft.DataCell(ft.Text("")),  # Empty Date
                    ft.DataCell(ft.Text(f"({journal[5]})")),  # Narration
                    ft.DataCell(ft.Text(""))  # Empty Amount
                ]
            )
            table_rows.append(row_3)

        table = ft.DataTable(
            width=page.window_width- 150,
            columns=[
                ft.DataColumn(ft.Text("Entry", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Date", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Particulars", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Amount", weight=ft.FontWeight.BOLD)),
            ],
            rows=table_rows,
        )

        return ft.Container(
            content=ft.ListView(
                [table],
                expand=1,
                spacing=10,
                padding=20,
                auto_scroll=True
            ),
            height=400,  # Adjust this value as needed
            expand=True,
        )

    def refresh_journal_table():
        nonlocal journal_table
        journal_table = create_journal_table()
        content.controls[-1] = journal_table
        page.update()

    def handle_dropdown_click(e):
        if e.control.text == "Add Journal":
            page.open(add_journal_menu())
            page.update()
        elif e.control.text == "Edit Journal":
            page.open(edit_journal_menu())
            page.update()
        elif e.control.text == "Delete Journal":
            page.open(delete_journal_menu())
            page.update()

    def handle_export_journal(e):
        success, message, path = export_journal_xlsx()
        show_banner(page, message, ft.colors.GREEN if success else ft.colors.RED, folder_path=path if success else None)


    title = ft.Text("Journal Entries", size=32, weight=ft.FontWeight.BOLD)
    actions_row = ft.Row(
        controls=[
            ft.ElevatedButton("Add Journal", on_click=handle_dropdown_click),
            ft.ElevatedButton("Edit Journal", on_click=handle_dropdown_click),
            ft.ElevatedButton("Delete Journal", on_click=handle_dropdown_click),
            ft.ElevatedButton("Export Journal", on_click=handle_export_journal),
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
    )
    journal_table = create_journal_table()

    content = ft.Column(
        controls=[
            title,
            actions_row,
            journal_table
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    return content

def ledger_page(page: ft.Page):
    def handle_export_ledger(e):
        success, message, path = export_ledger_xlsx()
        show_banner(page, message, ft.colors.GREEN if success else ft.colors.RED, folder_path=path if success else None)


    ledger_data = get_ledger_format()

    if ledger_data:
        tabs = []
        for account, data in ledger_data.items():
            table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text(col)) for col in data.columns
                ],
                rows=[
                    ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
                    for row in data.values.tolist()
                ]
            )
            tabs.append(ft.Tab(text=account, content=table))
        
        # Add export button for ledger
        export_button = ft.ElevatedButton(
            "Export Ledger",
            on_click=lambda e: handle_export_ledger(e)
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Ledger", size=32, weight=ft.FontWeight.BOLD),
                    export_button,  # Add the export button here
                    ft.Tabs(tabs=tabs),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    
    else:
        return ft.Container(
            content=ft.Text("No ledger data available. Please add some journal entries first."),
            alignment=ft.alignment.center,
            expand=True,
        )

def trial_balance_page(page: ft.Page):
    def handle_export_trial_balance(e):
        success, message, path = export_tb_xlsx()
        show_banner(page, message, ft.colors.GREEN if success else ft.colors.RED, folder_path=path if success else None)

    trial_balance_data = get_trial_balance()
    
    if trial_balance_data:
        table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Text("Particulars", size=20, weight=ft.FontWeight.BOLD),
                    numeric=False
                ),
                ft.DataColumn(
                    ft.Text("Debit", size=20, weight=ft.FontWeight.BOLD),
                    numeric=True
                ),
                ft.DataColumn(
                    ft.Text("Credit", size=20, weight=ft.FontWeight.BOLD),
                    numeric=True
                ),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(cell), size=16))
                        for cell in row
                    ]
                ) 
                for row in trial_balance_data
            ],
        )
        
        # Add export button for trial balance
        export_button = ft.ElevatedButton(
            "Export Trial Balance", 
            on_click=lambda e: handle_export_trial_balance(e)
        )


        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Trial Balance", size=32, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    export_button,
                    ft.Container(content=table, alignment=ft.alignment.center, expand=True),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
        )
    else:
        return ft.Container(
            content=ft.Text(
                "No data available for the trial balance. Please ensure you have journal entries and ledger data.",
                size=16, text_align=ft.TextAlign.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

def chatbot_page(page: ft.Page):
    chat_history = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
    
    def send_message(e):
        if not message_input.value:
            return
        
        user_message = message_input.value
        chat_history.controls.append(ft.Text(f"You: {user_message}"))
        message_input.value = ""
        page.update()
        
        # Get AI response
        ai_response = ask(user_message)
        chat_history.controls.append(ft.Text(f"AI: {ai_response}"))
        chat_history.controls.append(ft.Text("")) 
        page.update()
    
    message_input = ft.TextField(
        hint_text="Type your message here...",
        expand=True,
        on_submit=send_message
    )
    
    send_button = ft.IconButton(
        icon=ft.icons.SEND,
        on_click=send_message
    )
    
    # Load chat history
    history = get_history()
    for line in history:
        chat_history.controls.append(ft.Text(line))
    
    return ft.Column(
        [
            ft.Text("Chatbot", size=32, weight=ft.FontWeight.BOLD),
            chat_history,
            ft.Row(
                [message_input, send_button],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
        ],
        spacing=20,
        expand=True
    )

def settings_page(page: ft.Page):
    def handle_export_all_data(e):
        journal_success, journal_message, journal_path = export_journal_xlsx()
        ledger_success, ledger_message, ledger_path = export_ledger_xlsx()
        tb_success, tb_message, tb_path = export_tb_xlsx()

        if journal_success and ledger_success and tb_success:
            show_banner(page, "All data exported successfully.", ft.colors.GREEN , folder_path=journal_path)
        else:
            failed_exports = []
            if not journal_success:
                failed_exports.append("Journal")
            if not ledger_success:
                failed_exports.append("Ledger")
            if not tb_success:
                failed_exports.append("Trial Balance")
            show_banner(page,f"Failed to export: {', '.join(failed_exports)}", ft.colors.RED, folder_path = None)


    username = Account.signed_in_account()
    user_details = Account.get_user_info()

    if user_details:
        profile_section = ft.Column([
            ft.Text("Profile Information", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(f"Username: {username}", size=16),
            ft.Text(f"Email: {user_details['email']}", size=16),
            ft.Text(f"Phone Number: {user_details['phone_number']}", size=16),
            ft.Text(f"Date of Birth: {user_details['dob']}", size=16),
            ft.Divider(),
            ft.Text("Biography", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(user_details['biography'], size=16),
        ])

        if user_details['profile_picture']:
            try:
                temp_dir = tempfile.gettempdir()
                temp_image_path = os.path.join(temp_dir, f"profile_pic_{username}.png")
                
                with open(temp_image_path, 'wb') as f:
                    f.write(user_details['profile_picture'])
                
                profile_image = ft.Image(
                    src=temp_image_path,
                    width=256,
                    height=256,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.all(10),
                )
                
                def cleanup_temp_file():
                    try:
                        if os.path.exists(temp_image_path):
                            os.remove(temp_image_path)
                    except Exception as e:
                        print(f"Error cleaning up temporary file: {e}")
                
                page.window_destroy = cleanup_temp_file
                
            except Exception as e:
                print(f"Error loading profile picture: {e}")
                profile_image = ft.Container(
                    content=ft.Icon(ft.icons.PERSON, size=100),
                    width=256,
                    height=256,
                    bgcolor=ft.colors.GREY_300,
                    border_radius=ft.border_radius.all(10),
                    alignment=ft.alignment.center,
                )
        else:
            profile_image = ft.Container(
                content=ft.Icon(ft.icons.PERSON, size=100),
                width=256,
                height=256,
                bgcolor=ft.colors.GREY_300,
                border_radius=ft.border_radius.all(10),
                alignment=ft.alignment.center,
            )

        profile_row = ft.Row(
            [
                profile_image,
                ft.Container(
                    content=profile_section,
                    padding=ft.padding.only(left=20)
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        profile_row = ft.Row([
            profile_image,
            profile_section
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)

        actions_row = ft.Row([
                ft.ElevatedButton("Edit Profile", on_click=lambda _: page.go("edit_profile")),
                ft.ElevatedButton("Change Password", on_click=lambda _: page.go("change_password")),
                ft.ElevatedButton("Delete Account", on_click=lambda _: page.go("delete_account")),
                ft.ElevatedButton("Export All Data", on_click=lambda e: handle_export_all_data(e)),
            ])


        content = ft.Column([
            ft.Text("Settings", size=32, weight=ft.FontWeight.BOLD),
            profile_row,
            ft.Divider(),
            actions_row,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)

        return ft.Container(
            content=content,
            alignment=ft.alignment.center,
            expand=True,
            padding=50,
        )
    else:
        return ft.Text("Failed to fetch profile details.")

def edit_profile_page(page: ft.Page):
    user_details = Account.get_user_info()

    def handle_file_picker_result(e: ft.FilePickerResultEvent):
        try:
            if e.files and len(e.files) > 0:
                # Read the image file
                file_path = e.files[0].path
                with Image.open(file_path) as img:
                    # Resize image to a reasonable size
                    img.thumbnail((256, 256))
                    # Convert to bytes
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format=img.format)
                    profile_picture_data = img_byte_arr.getvalue()
                    return profile_picture_data
        except:
            return None
    
    file_picker = ft.FilePicker(
        on_result=handle_file_picker_result
    )
    page.overlay.append(file_picker)
    
    email_input = ft.TextField(label="Email", value=user_details['email'])
    phone_input = ft.TextField(label="Phone Number", value=user_details['phone_number'])
    dob_input = ft.CupertinoDatePicker(
        width=300, height=100,
        date_picker_mode=ft.CupertinoDatePickerMode.DATE,
        date_order = ft.CupertinoDatePickerDateOrder.DAY_MONTH_YEAR,
    )
    profile_pic_button = ft.ElevatedButton(
        "Upload Profile Picture",
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=['png', 'jpg', 'jpeg']
        )
    )
    bio_input = ft.TextField(label="Biography", value=user_details['biography'], multiline=True)

    def save_profile(e):
        updated_details = [
            email_input.value.strip(),
            dob_input.value,
            phone_input.value.strip(),
            handle_file_picker_result(e),
            bio_input.value.strip()
        ]
        success = Account.update_profile(updated_details[0], updated_details[1], updated_details[2], updated_details[3], updated_details[4])
        if success:
            show_banner(page, "Profile updated successfully!", ft.colors.GREEN)
            page.go("/settings")
        else:
            show_banner(page, "Failed to update profile.", ft.colors.RED)

    return ft.Column([
        ft.Text("Edit Profile", size=32, weight=ft.FontWeight.BOLD),
        email_input,
        phone_input,
        dob_input,
        bio_input,
        profile_pic_button,
        ft.ElevatedButton("Save Changes", on_click=save_profile),
        ft.ElevatedButton("Back to Settings", on_click=lambda _: page.go("/settings"))
    ], spacing=20)

def change_password_page(page: ft.Page):
    current_password = ft.TextField(label="Current Password", password=True)
    new_password = ft.TextField(label="New Password", password=True)
    confirm_password = ft.TextField(label="Confirm New Password", password=True)

    def change_password(e):
        if new_password.value != confirm_password.value:
            show_banner(page, "New passwords do not match.", ft.colors.RED)
            return

        success = Account.change_password(current_password.value.strip(), new_password.value.strip())
        if success:
            show_banner(page, "Password changed successfully!", ft.colors.GREEN)
            page.go("/settings")
        else:
            show_banner(page, "Failed to change password.", ft.colors.RED)

    return ft.Column([
        ft.Text("Change Password", size=32, weight=ft.FontWeight.BOLD),
        current_password,
        new_password,
        confirm_password,
        ft.ElevatedButton("Change Password", on_click=change_password),
        ft.ElevatedButton("Back to Settings", on_click=lambda _: page.go("/settings"))
    ], spacing=20)

def delete_account_page(page: ft.Page):
    password = ft.TextField(label="Enter your password to confirm", password=True)

    def delete_account(e):
        if Account.delete_account(password.value.strip()):
            show_banner(page, "Account deleted successfully.", ft.colors.GREEN)
            page.go("/login")  # Redirect to login page after account deletion
        else:
            show_banner(page, "Failed to delete account.", ft.colors.RED)

    return ft.Column([
        ft.Text("Delete Account", size=32, weight=ft.FontWeight.BOLD),
        ft.Text("Warning: This action cannot be undone.", color=ft.colors.RED),
        password,
        ft.ElevatedButton("Delete Account", on_click=delete_account, color=ft.colors.RED),
        ft.ElevatedButton("Back to Settings", on_click=lambda _: page.go("/settings"))
    ], spacing=20)

