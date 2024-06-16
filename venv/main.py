import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLineEdit, QButtonGroup, QMessageBox, QTableWidgetItem, QFileDialog, QHeaderView
from PyQt5.uic import loadUi
import resources_rc
import psycopg2
from PyQt5.QtCore import QObject, pyqtSignal, QTime, QDate, QDateTime, Qt
from PyQt5.QtGui import QFont, QPixmap, QColor
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import webbrowser
from urllib.parse import quote
import os
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
import re

class LoginScreen(QMainWindow):
    login_successful = pyqtSignal() # Define a signal for successful login

    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi(r"D:\JVFILES\UclicK\venv\login.ui", self)
        self.showpw.clicked.connect(self.toggle_password_visibility)
        self.login.clicked.connect(self.loginfunction)
        self.forgotpw.clicked.connect(self.forgot_password) 

    def toggle_password_visibility(self):   # Toggle the visibility of the password
        if self.password.echoMode() == QLineEdit.Password:
            self.password.setEchoMode(QLineEdit.Normal)
        else:
            self.password.setEchoMode(QLineEdit.Password)

    def loginfunction(self):    # Function to handle login
        user = self.username.text() # Get the entered username
        password = self.password.text() # Get the entered password

        if len(user) == 0 or len(password) == 0:
            self.error.setText("Please fill in all fields.") # Display error message if username or password is empty
            return
            return

        try:    # Connect to the PostgreSQL database
            conn = psycopg2.connect(
                host='localhost',
                dbname='UclicK',
                user='postgres',
                password='password',
            )

            cur = conn.cursor() # Create a cursor object
            
            # Execute a query to retrieve user information
            cur.execute("SELECT EMP_USERNAME, EMP_PASSWORD FROM EMPLOYEE WHERE EMP_USERNAME = %s AND EMP_PASSWORD = %s", (user, password))
            
            result = cur.fetchone() # Fetch the result

            if result and result[1] == password:
                self.login_successful.emit()    # Emit signal for successful login
                self.username.clear()   # Clear the username field
                self.password.clear()   # Clear the password field

            else:   # Display warning message for invalid login
                QMessageBox.warning(self, "Login", "Invalid username or password")
            # Close the cursor and connection
            cur.close() 
            conn.close()

        except psycopg2.Error as e: # Display error message for database connection error
            QMessageBox.critical(self, "Database Error", "Error connecting to the database: " + str(e))

    def forgot_password(self):  # Display information message for forgot password
        QMessageBox.information(self, "Forgot Password", "Oops! It seems like you've forgotten your password. Please contact the administrator to reset your password.")

class Dashboard(QMainWindow):
    logout_successful = pyqtSignal()    # Signal emitted upon successful logout
    
    def __init__(self):
        super(Dashboard, self).__init__()
        loadUi(r"D:\JVFILES\UclicK\venv\dashboard.ui", self)
        # List of sidebar buttons
        self.sidebar_buttons = [self.dashboard_button, self.appointments_button, self.clients_button, self.billing_button]
        self.current_index = 0  # Initialize the current index and set the initial page to the dashboard
        self.stackedWidget.setCurrentIndex(0) # Initially show dashboard

        # Dashboard - Connect buttons to their respective functions
        self.display_appointment_status_chart()  # Display appointment status chart
        self.display_total_appointments()
        self.display_total_clients()
        self.display_total_bills()
        self.dashboard_button.clicked.connect(self.show_dashboard)
        self.dashboard_button.clicked.connect(self.display_appointment_status_chart)

        # Appointments - Connect buttons to their respective functions
        self.appButton.clicked.connect(self.show_appointments)
        self.appointments_button.clicked.connect(self.show_all_appointments)
        self.appButton.clicked.connect(self.show_all_appointments)
        self.appointments_button.clicked.connect(self.update_pending_labels)
        self.appButton.clicked.connect(self.update_pending_labels)
        self.calendar.clicked.connect(self.update_time_slots)   # Calendar and Time Slots Setup
        self.update_time_slots(QDate.currentDate())             # Calendar and Time Slots Setup
        self.set_app_button.clicked.connect(self.handle_set_app_button_click)
        self.set_app_confirmButton.clicked.connect(self.confirm_new_appointment)
        self.set_app_cancelButton.clicked.connect(self.show_appointments)
        self.send_appButton.clicked.connect(self.send_appointment_email)
        self.app_set_closeButton.clicked.connect(self.show_appointments)
        self.app_viewButton.clicked.connect(self.view_appointment)
        self.view_apppetite_closeButton.clicked.connect(self.show_appointments)
        self.view_appclassic_closeButton.clicked.connect(self.show_appointments)
        self.app_petite_pending.clicked.connect(self.show_petite_pending_appointments)
        self.apppetite_pending_nextButton.clicked.connect(self.next_petite_pending_appointment)
        self.apppetite_pending_backButton.clicked.connect(self.prev_petite_pending_appointment)
        self.apppetite_pending_cancelButton.clicked.connect(self.cancel_petite_pending_appointment)
        self.apppetite_pending_noshowButton.clicked.connect(self.noshow_petite_pending_appointment)
        self.apppetite_pending_reschedButton.clicked.connect(self.resched_petite_pending_appointment)
        self.apppetite_resched_cancelButton.clicked.connect(self.show_petite_pending_appointments)
        self.apppetite_resched_saveButton.clicked.connect(self.petite_reschedule_save_button_clicked)
        self.apppetite_pending_completeButton.clicked.connect(self.complete_petite_pending_appointment)
        self.apppetite_pending_closeButton.clicked.connect(self.show_appointments)
        self.app_petite_complete.clicked.connect(self.show_petite_complete_appointments)
        self.apppetite_complete_backButton.clicked.connect(self.prev_petite_complete_appointment)
        self.apppetite_complete_nextButton.clicked.connect(self.next_petite_complete_appointment)
        self.apppetite_complete_undoButton.clicked.connect(self.undo_petite_complete_appointment)
        self.apppetite_complete_closeButton.clicked.connect(self.show_appointments)
        self.app_classic_pending.clicked.connect(self.show_classic_pending_appointments)
        self.appclassic_pending_nextButton.clicked.connect(self.next_classic_pending_appointment)
        self.appclassic_pending_backButton.clicked.connect(self.prev_classic_pending_appointment)
        self.appclassic_pending_cancelButton.clicked.connect(self.cancel_classic_pending_appointment)
        self.appclassic_pending_noshowButton.clicked.connect(self.noshow_classic_pending_appointment)
        self.appclassic_pending_reschedButton.clicked.connect(self.resched_classic_pending_appointment)
        self.appclassic_resched_cancelButton.clicked.connect(self.show_classic_pending_appointments)
        self.appclassic_resched_saveButton.clicked.connect(self.classic_reschedule_save_button_clicked)
        self.appclassic_pending_completeButton.clicked.connect(self.complete_classic_pending_appointment)
        self.appclassic_pending_closeButton.clicked.connect(self.show_appointments)
        self.app_classic_complete.clicked.connect(self.show_classic_complete_appointments)
        self.appclassic_complete_backButton.clicked.connect(self.prev_classic_complete_appointment)
        self.appclassic_complete_nextButton.clicked.connect(self.next_classic_complete_appointment)
        self.appclassic_complete_undoButton.clicked.connect(self.undo_classic_complete_appointment)
        self.appclassic_complete_closeButton.clicked.connect(self.show_appointments)
        self.search_app_button.clicked.connect(self.search_appointments)
        self.delete_app_button.clicked.connect(self.delete_app)
        self.send_app_button.clicked.connect(self.send_email_for_appointment)
        self.appsbackButton.clicked.connect(self.reset_appointments_table)
        # Initialize lists and indices for managing appointments
        self.current_pending_petite_appointment_index = 0
        self.petite_pending_appointments = []
        self.current_pending_classic_appointment_index = 0
        self.classic_pending_appointments = []
        self.current_complete_petite_appointment_index = 0
        self.petite_complete_appointments = []
        self.current_complete_classic_appointment_index = 0
        self.classic_complete_appointments = []

        # Clients - Connect buttons to their respective functions
        self.clientButton.clicked.connect(self.show_clients)
        # Initialize lists and indices for managing clients
        self.current_client_info_index = []
        self.client_info = []
        self.current_client_edit_index = []
        self.client_edit = []
        self.current_archived_client_info_index = []
        self.archived_client_info = []
        self.switch_to_archived_clientsButton.clicked.connect(self.load_archived_clients)
        self.archive_button.clicked.connect(self.archive_client)
        self.client_histButton.clicked.connect(self.client_appointment_history)
        self.apphist_closeButton.clicked.connect(self.show_clients)
        self.search_apphist_button.clicked.connect(self.search_client_app_hist)
        self.apphistbackbutton.clicked.connect(self.reset_apphist_table)
        self.client_editButton.clicked.connect(self.edit_client_info)
        self.client_editinfo_cancelButton.clicked.connect(self.show_clients)
        self.client_editinfo_saveButton.clicked.connect(self.confirm_save_changes)
        self.client_viewButton.clicked.connect(self.view_client_info)
        self.clientinfo_backButton.clicked.connect(self.prev_client_info)
        self.clientinfo_nextButton.clicked.connect(self.next_client_info)
        self.clientsbackbutton.clicked.connect(self.reset_clients_table)
        # Archived Clients - Connect buttons to their respective functions
        self.switch_to_active_clientsButton.clicked.connect(self.load_clients_data)
        self.restore_button.clicked.connect(self.restore_client)
        self.archived_client_histButton.clicked.connect(self.archived_client_appointment_history)     
        self.archived_apphist_closeButton.clicked.connect(self.load_archived_clients) 
        self.search_archived_apphist_button.clicked.connect(self.search_archived_client_app_hist)
        self.archived_apphistbackbutton.clicked.connect(self.reset_archived_apphist_table)
        self.archived_client_viewButton.clicked.connect(self.view_archived_client_info)
        self.archived_clientinfo_backButton.clicked.connect(self.prev_archived_client_info)
        self.archived_clientinfo_nextButton.clicked.connect(self.next_archived_client_info)
        self.clientinfo_closeButton.clicked.connect(self.show_clients)
        self.archived_clientinfo_closeButton.clicked.connect(self.load_archived_clients)
        self.billButton.clicked.connect(self.show_billing)
        self.appointments_button.clicked.connect(self.show_appointments)
        self.clients_button.clicked.connect(self.show_clients)
        self.search_client_button.clicked.connect(self.search_clients)
        self.search_archived_client_button.clicked.connect(self.search_archived_clients)
        self.archived_clientsbackbutton.clicked.connect(self.reset_archived_clients_table)

        # Billing - Connect buttons to their respective functions
        self.billing_button.clicked.connect(self.show_billing)
        self.search_bill_button.clicked.connect(self.search_bills)
        self.billbackbutton.clicked.connect(self.reset_bill_table)
        self.generate_bill_button.clicked.connect(self.generate_bill)
        self.clear_button.clicked.connect(self.clear_fields)
        self.delete_button.clicked.connect(self.delete_bill)
        self.download_button.clicked.connect(self.download_bill)
        self.send_button.clicked.connect(self.send_bill_to_email)
        self.logout_button.clicked.connect(self.show_logout_confirmation)
         
    def show_dashboard(self):   # Switch to the dashboard screen
        self.stackedWidget.setCurrentIndex(0)
        self.current_index = 0
        self.dashboard_button.setChecked(True)
        self.previous_button_index = 0
        
    def display_appointment_status_chart(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*), APP_STATUS FROM APPOINTMENT GROUP BY APP_STATUS")
            status_counts = cur.fetchall()
            
            counts = [0, 0, 0, 0]   # Initialize counts for the four categories
            status_names = ['Pending', 'Cancelled', 'No Show', 'Complete']

            status_map = {  # Map the actual status names to the index in the counts array
                'pending': 0,
                'rescheduled': 0,
                'cancelled': 1,
                'no show': 2,
                'complete': 3
            }

            for status_count in status_counts:
                status_name = status_count[1].lower()  # Convert to lowercase to avoid case mismatch
                count = status_count[0]
                if status_name in status_map:
                    index = status_map[status_name]
                    counts[index] += count

            # Define colors for the categories
            colors = ['#F5D547', '#D9534F', '#F0A500', '#4CAF50']  # Colors in order: (Pending, Cancelled, No Show, Complete)

            # Check if all counts are zero
            if all(count == 0 for count in counts):
                # Handle case where there are no appointments
                no_data_message = "No appointments found."

                # Plotting a text annotation in the center of the figure
                fig, ax = plt.subplots(figsize=(6.01, 3.51))
                ax.text(0.5, 0.5, no_data_message, va='center', ha='center', fontsize=14, color='gray')
                ax.axis('off')  # Turn off axes for a cleaner look
                
                # Save the chart as an image with a transparent background
                plt.savefig('app_status_pie_chart.png', transparent=True, bbox_inches='tight', pad_inches=0)
            else:                
                # Plot pie chart
                plt.clf()
                plt.figure(figsize=(6.01, 3.51))
                plt.pie(counts, colors=colors, autopct='%.1f%%', startangle=140, textprops={'color': 'white', 'fontsize': 12})
                plt.axis('equal')
                plt.savefig('app_status_pie_chart.png', transparent=True)  # Save the chart as an image with a transparent background

            # Display the chart in a QLabel
            pixmap = QPixmap('app_status_pie_chart.png')
            self.appointment_status_chart.setPixmap(pixmap)
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error connecting to the database: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def display_total_appointments(self):   # Display total appointments
        conn = None
        try:    # Database connection and data retrieval code...
            conn = self.create_database_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM APPOINTMENT")
            total_appointments = cur.fetchone()[0]
            self.appLabel.setText(str(total_appointments))
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error connecting to the database: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def display_total_clients(self):    # Display total clients
        conn = None
        try:    # Database connection and data retrieval code...
            conn = self.create_database_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM CLIENT")
            total_clients = cur.fetchone()[0]
            self.clientLabel.setText(str(total_clients))
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error connecting to the database: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def display_total_bills(self):  # Display total bills
        conn = None
        try:    # Database connection and data retrieval code...
            conn = self.create_database_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM BILL")
            total_bills = cur.fetchone()[0]
            self.billLabel.setText(str(total_bills))
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error connecting to the database: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()
            
    def show_appointments(self):    # Switch to the appointments screen
        self.stackedWidget.setCurrentIndex(1)
        self.current_index = 1
        self.appointments_button.setChecked(True) 
        self.previous_button_index = 1

    def show_all_appointments(self):    # Show all appointments
        conn = None
        try:    # Database connection and data retrieval code...
            conn = self.create_database_connection()
            cur = conn.cursor() 
            cur.execute("""
                SELECT 
                    APP_NUM, 
                    CLIENT.client_fname || ' ' || CLIENT.client_lname AS client_name, 
                    CLIENT.client_email,
                    APP_PACKAGE,
                    APP_DATE, 
                    APP_TIME, 
                    APP_ADDRESS, 
                    APP_STATUS 
                FROM 
                    APPOINTMENT 
                JOIN 
                    CLIENT 
                ON 
                    APPOINTMENT.CLIENT_CODE = CLIENT.CLIENT_CODE
                ORDER BY 
                APP_DATE DESC, 
                APP_TIME DESC
            """)
            result = cur.fetchall() 
            
            self.appTable.setRowCount(len(result))
            self.appTable.setColumnCount(8)  # Adjust the column count
            column_names = ['Appointment Number', 'Client', 'Client email', 'Package', 'Date', 'Time', 'Address', 'Status']
            self.appTable.setHorizontalHeaderLabels(column_names)
            font = QFont()
            font.setBold(True)
            font.setPointSize(12) 
            self.appTable.horizontalHeader().setFont(font)
            
            for row_index, row_data in enumerate(result):
                for col_index, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    self.appTable.setItem(row_index, col_index, item)

            # Resize columns to fit contents
            self.appTable.resizeColumnsToContents()
            self.appTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error loading appointments: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def update_pending_labels(self):    # Update labels for pending appointments
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor() 

            # Query for counting appointments to review for each package
            cur.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE app_status IN ('Pending', 'Rescheduled') AND app_package = 'Petite'")
            count_petite_app_pending = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE app_status = 'Complete' AND app_package = 'Petite'")
            count_petite_app_completed = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE app_status IN ('Pending', 'Rescheduled') AND app_package = 'Classic'")
            count_classic_app_pending = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE app_status = 'Complete' AND app_package = 'Classic'")
            count_classic_app_completed = cur.fetchone()[0]

            # Update labels
            self.app_petite_pending_label.setText(f"{count_petite_app_pending} appointments to review")
            self.app_petite_completed_label.setText(f"{count_petite_app_completed} appointments to review")
            self.app_classic_pending_label_.setText(f"{count_classic_app_pending} appointments to review")
            self.app_classic_completed_label.setText(f"{count_classic_app_completed} appointments to review")

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error updating pending labels: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def update_time_slots(self, date):  # Method to update available time slots based on selected date
        self.time_slots_table.clearContents()

        # Define time slots from 11:00 AM to 6:30 PM with 30 mins interval
        start_time = QTime(11, 0)
        end_time = QTime(18, 30)
        interval = 30

        time_slots = []
        time = start_time
        while time <= end_time:
            time_slots.append(time.toString('h:mm AP'))
            time = time.addSecs(interval * 60)

        self.time_slots_table.setRowCount(8)
        self.time_slots_table.setColumnCount(4)
        self.time_slots_table.setHorizontalHeaderLabels(["Time", "Status", "Time", "Status"])

        # Manually set the column widths to fit the table width
        table_width = 300
        column_width = table_width // 4
        for col in range(4):
            self.time_slots_table.setColumnWidth(col, column_width)

        conn = self.create_database_connection()
        if not conn:
            return

        try:
            cur = conn.cursor()
            query = "SELECT app_time, app_status FROM appointment WHERE app_date = %s"
            cur.execute(query, (date.toString('yyyy-MM-dd'),))
            appointments = cur.fetchall()

            # Extract the starting time from each appointment time range and store in a set for fast lookup
            scheduled_times = {app_time.split(' - ')[0] for app_time, app_status in appointments}

            for i in range(8):
                # First column set
                time1 = time_slots[i]
                status1 = "Scheduled" if time1 in scheduled_times else "Available"
                item1 = QTableWidgetItem(time1)
                status_item1 = QTableWidgetItem(status1)
                if status1 == "Scheduled":
                    status_item1.setBackground(QColor(255, 165, 0))    # Light orange for Scheduled
                    status_item1.setForeground(QColor(0, 0, 0))        # Black text
                else:
                    status_item1.setBackground(QColor(144, 238, 144))  # Light green for Available
                    status_item1.setForeground(QColor(0, 0, 0))        # Black text
                self.time_slots_table.setItem(i, 0, item1)
                self.time_slots_table.setItem(i, 1, status_item1)

                # Second column set
                if (i + 8) < len(time_slots):
                    time2 = time_slots[i + 8]
                    status2 = "Scheduled" if time2 in scheduled_times else "Available"
                else:
                    time2 = ""
                    status2 = ""
                item2 = QTableWidgetItem(time2)
                status_item2 = QTableWidgetItem(status2)
                if status2 == "Scheduled":
                    status_item2.setBackground(QColor(255, 165, 0))    # Light orange for Scheduled
                    status_item2.setForeground(QColor(0, 0, 0))        # Black text
                else:
                    status_item2.setBackground(QColor(144, 238, 144))  # Light green for Available
                    status_item2.setForeground(QColor(0, 0, 0))        # Black text
                self.time_slots_table.setItem(i, 2, item2)
                self.time_slots_table.setItem(i, 3, status_item2)

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error fetching data from the database: " + str(e))
        finally:
            cur.close()
            conn.close()

    def handle_set_app_button_click(self):
        selected_date = self.calendar.selectedDate()
        current_date = QDate.currentDate()
        current_time = QTime.currentTime()

        if selected_date < current_date:
            QMessageBox.information(self, "Invalid Date", "Cannot select a past date for a new appointment.")
            return
        
        selected_items = self.time_slots_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select an available time slot.")
            return

        selected_item = selected_items[0]
        row = selected_item.row()
        column = selected_item.column()

        if column % 2 == 1:  # Ensure the selected cell is a status cell
            time_slot = self.time_slots_table.item(row, column - 1).text()
            status = selected_item.text()
        else:
            time_slot = selected_item.text()
            status = self.time_slots_table.item(row, column + 1).text()

        if selected_date == current_date:
            # Extract the start time from the time slot
            slot_time_str = time_slot.split(" - ")[0].strip()
            slot_time = QTime.fromString(slot_time_str, "h:mm AP")

            if slot_time < current_time:
                QMessageBox.information(self, "Invalid Time", "Cannot select a past time slot for a new appointment.")
                return

        if status == "Scheduled":
            QMessageBox.information(self, "Time Slot Unavailable", "The selected time slot is already scheduled.")
        else:
            self.set_new_appointment(time_slot)

    def set_new_appointment(self, time_slot):   # Method to manage setting new appointments
        date = self.calendar.selectedDate()
        formatted_date = date.toString('yyyy-MM-dd')

        self.app_date.setText(formatted_date)
        self.app_time.setText(time_slot)

        # Clear previous inputs
        self.app_cli_fname.clear()
        self.app_cli_lname.clear()
        self.app_cli_contact.clear()
        self.app_cli_email.clear()
        self.app_notes.clear()
        self.checkBox_selectPetite.setChecked(False)
        self.checkBox_selectClassic.setChecked(False)

        self.stackedWidget.setCurrentIndex(2)

    def confirm_new_appointment(self):  # Method to validate and confirm new appointment creation
        # Gather input values
        fname = self.app_cli_fname.text().strip()
        lname = self.app_cli_lname.text().strip()
        contact = self.app_cli_contact.text().strip()
        email = self.app_cli_email.text().strip()
        date = self.app_date.text()
        time_slot = self.app_time.text()
        notes = self.app_notes.toPlainText().strip()
        package = 'Petite' if self.checkBox_selectPetite.isChecked() else 'Classic' if self.checkBox_selectClassic.isChecked() else None
        
        if not (fname and lname and contact and email and package): # Validate required fields
            QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return

        if not self.is_valid_email(email):  # Validate email format
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
            return
        
        # Gather employee input values
        emp_fname = self.app_emp_fname.text().strip()
        emp_lname = self.app_emp_lname.text().strip()

        if not (emp_fname and emp_lname):  # Check if employee name fields are filled
            QMessageBox.warning(self, "Input Error", "Please enter employee first name and last name.")
            return

        # Confirm the action
        confirmation = QMessageBox.question(self, "Confirm Appointment", "Do you want to set this appointment?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            # Proceed with appointment creation
            self.insert_appointment(fname, lname, contact, email, date, time_slot, package, emp_fname, emp_lname)

    def is_valid_email(self, email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None

    def insert_appointment(self, fname, lname, contact, email, date, time_slot, package, emp_fname, emp_lname):
        try:
            conn = self.create_database_connection()
            cur = conn.cursor()

            # Generate unique IDs
            app_num = self.generate_appointment_num()
            client_code = self.generate_client_code(fname, lname)

            # Check if the client already exists
            client_code = self.insert_or_get_client(cur, client_code, fname, lname, contact, email)

            # Calculate end time
            start_time = QTime.fromString(time_slot, 'h:mm AP')
            duration = 15 if package == 'Petite' else 30
            end_time = start_time.addSecs(duration * 60).toString('h:mm AP')
            app_time = f"{time_slot} - {end_time}"

            # Retrieve emp_code based on emp_fname and emp_lname
            emp_fname = self.app_emp_fname.text().strip()
            emp_lname = self.app_emp_lname.text().strip()

            try:
                cur.execute("SELECT emp_code FROM employee WHERE emp_fname = %s AND emp_lname = %s", (emp_fname, emp_lname))
                result = cur.fetchone()
                if result:
                    emp_code = result[0]
                else:
                    QMessageBox.warning(self, "Employee Not Found", "The specified employee could not be found.")
                    return
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error fetching employee code: " + str(e))
                return

            # Insert new appointment
            app_address = '2F City Time Square Mactan, Basak, Lapu-Lapu City, Philippines'
            cur.execute("""
                INSERT INTO APPOINTMENT (app_num, client_code, app_date, app_time, app_address, app_status, app_package, emp_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (app_num, client_code, date, app_time, app_address, 'Pending', package, emp_code))
            
            conn.commit()
            QMessageBox.information(self, "Success", "Appointment set successfully.")
            # Update the labels after successfully inserting the appointment
            self.update_pending_labels()
            self.display_total_appointments()
            self.stackedWidget.setCurrentIndex(3)  

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error inserting appointment: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def generate_appointment_num(self):
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_client_code(self, fname, lname):   
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{fname[0]}{current_datetime}{lname[0]}"

    def insert_or_get_client(self, cur, client_code, fname, lname, contact, email): 
        cur.execute("SELECT client_code FROM CLIENT WHERE client_email = %s", (email,))
        existing_client = cur.fetchone()
        if existing_client:
            return existing_client[0]

        # Insert new client
        cur.execute("""
            INSERT INTO CLIENT (client_code, client_fname, client_lname, client_contact_number, client_email)
            VALUES (%s, %s, %s, %s, %s)
        """, (client_code, fname, lname, contact, email))
        return client_code
    
    def send_appointment_email(self):   # Method to send confirmation emails to clients
        # Gather necessary details
        client_email = self.app_cli_email.text().strip()
        fname = self.app_cli_fname.text().strip()
        lname = self.app_cli_lname.text().strip()
        date = self.app_date.text()
        time_slot = self.app_time.text()
        package = 'Petite (15 minutes)' if self.checkBox_selectPetite.isChecked() else 'Classic (30 minutes)' if self.checkBox_selectClassic.isChecked() else None
        notes = self.app_notes.toPlainText().strip()
        
        if not client_email:
            QMessageBox.warning(self, "Input Error", "Please enter the client's email address.")
            return
        
        # Email subject and body
        subject = "Appointment Confirmation"
        body = f"Dear {fname} {lname},\n\n" \
               f"Your appointment has been scheduled as follows:\n" \
               f"Date: {date}\n" \
               f"Time: {time_slot}\n" \
               f"Package: {package}\n" \
               f"Notes: {notes}\n\n" \
               f"Thank you,\n" \
               f"Uclick Self-Portrait Studio"

        # Construct the URL for composing the email in Gmail
        url = "https://mail.google.com/mail/?view=cm&to={}&su={}&body={}".format(
            quote(client_email), quote(subject), quote(body)
        )

        webbrowser.open(url)    # Open the web browser with the URL

    def view_appointment(self): # Method to retrieve and display appointment details
        date = self.calendar.selectedDate().toString('yyyy-MM-dd')  # Get the selected date
        selected_items = self.time_slots_table.selectedItems()  # Get the selected items from the time slots table
        
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a time slot.")
            return
        
        # Determine the selected time slot and status
        selected_item = selected_items[0]
        row = selected_item.row()
        column = selected_item.column()

        if column % 2 == 1:  # Ensure the selected cell is a status cell
            time_slot = self.time_slots_table.item(row, column - 1).text()
            status = selected_item.text()
        else:
            time_slot = selected_item.text()
            status = self.time_slots_table.item(row, column + 1).text()

        if status == "Available":
            QMessageBox.information(self, "No Appointment", "No appointment to preview for the selected time slot.")
            return

        # Retrieve appointment details from the database
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor()
            query = """
                SELECT app_date, app_time, app_package, client_fname, client_lname
                FROM appointment
                JOIN client ON appointment.client_code = client.client_code
                WHERE app_date = %s AND app_time LIKE %s
            """
            cur.execute(query, (date, f"{time_slot}%"))
            appointment = cur.fetchone()

            if appointment:
                app_date, app_time, app_package, client_fname, client_lname = appointment
                client_name = f"{client_fname} {client_lname}"
                datetime_info = f"{app_date}  {app_time}"

                if app_package == "Petite":
                    self.stackedWidget.setCurrentIndex(4)
                    self.view_apppetite_client_label.setText(client_name)
                    self.view_apppetite_datetime_label.setText(datetime_info)
                elif app_package == "Classic":
                    self.stackedWidget.setCurrentIndex(5)
                    self.view_appclassic_client_label.setText(client_name)
                    self.view_appclassic_datetime_label.setText(datetime_info)
            else:
                QMessageBox.warning(self, "No Appointment", "No appointment found for the selected time slot.")

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error retrieving appointment details: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def show_petite_pending_appointments(self): # Method to display pending appointments for the "Petite" package
        self.stackedWidget.setCurrentIndex(6)
        self.petite_pending_appointments = self.fetch_petite_pending_appointments()
        self.current_pending_petite_appointment_index = 0
        self.display_petite_pending_appointment(self.current_pending_petite_appointment_index)

    def fetch_petite_pending_appointments(self): # Method to retrieve pending "Petite" appointments from the database 
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor() 
            cur.execute("SELECT * FROM APPOINTMENT WHERE app_status IN ('Pending', 'Rescheduled') AND app_package = 'Petite'")
            return cur.fetchall()
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error loading petite pending appointments: " + str(e))
            return []
        finally:
            if conn:
                cur.close()
                conn.close()

    def display_petite_pending_appointment(self, index): # Method to display details of the selected pending appointment
        if index < len(self.petite_pending_appointments):
            appointment = self.petite_pending_appointments[index]
            client_code = appointment[1]  # Assuming appointment[2] is the client_code
            client_fname, client_lname = self.fetch_client_details(client_code)

            if client_fname and client_lname:
                self.apppetite_pending_client_label.setText(f"{client_fname} {client_lname}")
            else:
                self.apppetite_pending_client_label.setText("Unknown Client")
                
            self.apppetite_pending_datetime_label.setText(f"{appointment[2]}  {appointment[3]}")
        else:
            QMessageBox.warning(self, "Warning", "No more pending appointments to display.")

    def fetch_client_details(self, client_code):    # Method to retrieve client details based on their client code
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor() 
            cur.execute("SELECT client_fname, client_lname FROM CLIENT WHERE client_code = %s", (client_code,))
            client_details = cur.fetchone()
            if client_details:
                return client_details[0], client_details[1]
            else:
                return None, None
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error fetching client details: " + str(e))
            return None, None
        finally:
            if conn:
                cur.close()
                conn.close()

    def next_petite_pending_appointment(self):  # Method to display the next pending "Petite" appointment
        self.current_pending_petite_appointment_index += 1
        self.display_petite_pending_appointment(self.current_pending_petite_appointment_index)

    def prev_petite_pending_appointment(self):  # Method to display the previous pending "Petite" appointment
        if self.current_pending_petite_appointment_index > 0:
            self.current_pending_petite_appointment_index -= 1
            self.display_petite_pending_appointment(self.current_pending_petite_appointment_index)
        else:
            QMessageBox.warning(self, "Warning", "This is the first pending appointment.")

    def cancel_petite_pending_appointment(self):    # Method to cancel the selected pending "Petite" appointment
        confirmation = QMessageBox.question(self, "Cancel Appointment", "Are you sure you want to cancel this appointment?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            appointment = self.petite_pending_appointments[self.current_pending_petite_appointment_index]  # Get the current pending appointment
            
            # Update the status to 'Cancelled' in the database
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor() 
                cur.execute("UPDATE APPOINTMENT SET app_status = 'Cancelled' WHERE app_num = %s", (appointment[0],))
                conn.commit()
                QMessageBox.information(self, "Cancellation", "Appointment Cancelled Successfully")
                
                self.petite_pending_appointments.pop(self.current_pending_petite_appointment_index)  # Remove the cancelled appointment from the list
                
                self.update_pending_labels()
                self.show_all_appointments()
                
                # Display next pending appointment if available
                if self.current_pending_petite_appointment_index < len(self.petite_pending_appointments):
                    self.display_petite_pending_appointment(self.current_pending_petite_appointment_index)
                elif self.current_pending_petite_appointment_index > 0:
                    self.current_pending_petite_appointment_index -= 1
                    self.display_petite_pending_appointment(self.current_pending_petite_appointment_index)
                else:
                    self.apppetite_pending_client_label.clear()
                    self.apppetite_pending_datetime_label.clear()
                    QMessageBox.warning(self, "Warning", "No more pending appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error cancelling appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def noshow_petite_pending_appointment(self): # Method to mark the selected pending "Petite" appointment as "No Show"
        confirmation = QMessageBox.question(self, "Appointment No Show", "Are you sure you want to mark this appointment as 'No Show'?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            appointment = self.petite_pending_appointments[self.current_pending_petite_appointment_index]  # Get the current pending appointment
            
            # Update the status to 'Cancelled' in the database
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor() 
                cur.execute("UPDATE APPOINTMENT SET app_status = 'No Show' WHERE app_num = %s", (appointment[0],))
                conn.commit()
                QMessageBox.information(self, "No Show", "The appointment has been successfully marked as 'No Show'.")
                
                self.petite_pending_appointments.pop(self.current_pending_petite_appointment_index)  # Remove the no show appointment from the list
                
                self.update_pending_labels()
                self.show_all_appointments()
                
                # Display next pending appointment if available
                if self.current_pending_petite_appointment_index < len(self.petite_pending_appointments):
                    self.display_petite_pending_appointment(self.current_pending_petite_appointment_index)
                elif self.current_pending_petite_appointment_index > 0:
                    self.current_pending_petite_appointment_index -= 1
                    self.display_petite_pending_appointment(self.current_pending_petite_appointment_index)
                else:
                    self.apppetite_pending_client_label.clear()
                    self.apppetite_pending_datetime_label.clear()
                    QMessageBox.warning(self, "Warning", "No more pending appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error cancelling appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def resched_petite_pending_appointment(self): # Method to allow rescheduling of the selected pending "Petite" appointment
        self.stackedWidget.setCurrentIndex(7)

        # Retrieve current pending appointment
        if self.current_pending_petite_appointment_index < len(self.petite_pending_appointments):
            appointment = self.petite_pending_appointments[self.current_pending_petite_appointment_index]
            client_code = appointment[1]
            client_fname, client_lname = self.fetch_client_details(client_code)

            if client_fname and client_lname:
                self.apppetite_resched_client_label.setText(f"{client_fname} {client_lname}")
            else:
                self.apppetite_resched_client_label.setText("Unknown Client")
            self.apppetite_resched_origdatetime.setText(f"{appointment[2]}  {appointment[3]}")

            current_datetime = QDateTime.currentDateTime()
            self.apppetite_resched_datetime.setDateTime(current_datetime)
                
        else:
            QMessageBox.warning(self, "Warning", "No pending appointment to reschedule.")

    def petite_reschedule_save_button_clicked(self): # Method to saves changes made during rescheduling
        confirmation = QMessageBox.question(self, "Confirmation", "Are you sure you want to save changes?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            # Retrieve current pending appointment
            if self.current_pending_petite_appointment_index < len(self.petite_pending_appointments):
                appointment = self.petite_pending_appointments[self.current_pending_petite_appointment_index]
                new_datetime = self.apppetite_resched_datetime.dateTime()
                new_date = new_datetime.toString("yyyy-MM-dd")
                new_start_time = new_datetime.toString("h:mm AP")  # Format time as 12-hour with AM/PM
                new_end_time = new_datetime.addSecs(15 * 60).toString("h:mm AP")  # End time
                new_time_range = f"{new_start_time} - {new_end_time}"
                # Update the database with new date and time
                conn = None
                try:
                    conn = self.create_database_connection()
                    cur = conn.cursor()
                    cur.execute("UPDATE APPOINTMENT SET app_date = %s, app_time = %s, app_status = 'Rescheduled' WHERE app_num = %s",
                                (new_date, new_time_range, appointment[0]))
                    conn.commit()
                    QMessageBox.information(self, "Success", "Appointment rescheduled successfully.")

                    self.show_all_appointments()
                    self.show_petite_pending_appointments()

                except psycopg2.Error as e:
                    QMessageBox.critical(self, "Database Error", "Error updating appointment: " + str(e))
                finally:
                    if conn:
                        cur.close()
                        conn.close()
            else:
                QMessageBox.warning(self, "Warning", "No pending appointment to reschedule.")

    def complete_petite_pending_appointment(self): # Method to mark the selected pending "Petite" appointment as "Complete"
        confirmation = QMessageBox.question(self, "Appointment Complete", "Are you sure you want to mark this appointment as 'Complete'?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            appointment = self.petite_pending_appointments[self.current_pending_petite_appointment_index]  # Get the current pending appointment
            
            # Update the status to 'Complete' in the database
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor() 
                cur.execute("UPDATE APPOINTMENT SET app_status = 'Complete' WHERE app_num = %s", (appointment[0],))
                conn.commit()
                QMessageBox.information(self, "Complete", "The appointment has been successfully marked as 'Complete'.")
                
                self.petite_pending_appointments.pop(self.current_pending_petite_appointment_index)  # Remove the completed appointment from the list
                
                self.update_pending_labels()
                self.show_all_appointments()
                
                # Display next pending appointment if available
                if self.current_pending_petite_appointment_index < len(self.petite_pending_appointments):
                    self.display_petite_pending_appointment(self.current_pending_petite_appointment_index)
                elif self.current_pending_petite_appointment_index > 0:
                    self.current_pending_petite_appointment_index -= 1
                    self.display_petite_pending_appointment(self.current_pending_petite_appointment_index)
                else:
                    self.apppetite_pending_client_label.clear()
                    self.apppetite_pending_datetime_label.clear()
                    QMessageBox.warning(self, "Warning", "No more pending appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error cancelling appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def show_petite_complete_appointments(self):
        self.stackedWidget.setCurrentIndex(10)
        self.petite_complete_appointments = self.fetch_petite_complete_appointments()
        self.current_complete_petite_appointment_index = 0
        self.display_petite_complete_appointment(self.current_complete_petite_appointment_index)

    def fetch_petite_complete_appointments(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor() 
            cur.execute("SELECT * FROM APPOINTMENT WHERE app_status = 'Complete' AND app_package = 'Petite'")
            return cur.fetchall()
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error loading petite complete appointments: " + str(e))
            return []
        finally:
            if conn:
                cur.close()
                conn.close()

    def display_petite_complete_appointment(self, index):
        if index < len(self.petite_complete_appointments):
            appointment = self.petite_complete_appointments[index]
            client_code = appointment[1]  
            client_fname, client_lname = self.fetch_client_details(client_code)

            if client_fname and client_lname:
                self.apppetite_complete_client_label.setText(f"{client_fname} {client_lname}")
            else:
                self.apppetite_complete_client_label.setText("Unknown Client")
                
            self.apppetite_complete_datetime_label.setText(f"{appointment[2]}  {appointment[3]}")
        else:
            QMessageBox.warning(self, "Warning", "No more complete appointments to display.")

    def next_petite_complete_appointment(self):
        self.current_complete_petite_appointment_index += 1
        self.display_petite_complete_appointment(self.current_complete_petite_appointment_index)

    def prev_petite_complete_appointment(self):
        if self.current_complete_petite_appointment_index > 0:
            self.current_complete_petite_appointment_index -= 1
            self.display_petite_complete_appointment(self.current_complete_petite_appointment_index)
        else:
            QMessageBox.warning(self, "Warning", "This is the first complete appointment.")

    def undo_petite_complete_appointment(self):
        confirmation = QMessageBox.question(self, "Confirmation", "Are you sure you want to undo the complete appointment?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            appointment = self.petite_complete_appointments[self.current_complete_petite_appointment_index]  # Get the current complete appointment
            
            # Update the status to 'Pending' in the database
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor() 
                cur.execute("UPDATE APPOINTMENT SET app_status = 'Pending' WHERE app_num = %s", (appointment[0],))
                conn.commit()
                QMessageBox.information(self, "Success", "Appointment successfully undone.")
                
                self.petite_complete_appointments.pop(self.current_complete_petite_appointment_index)  # Remove the undone appointment from the list
                
                self.update_pending_labels()
                self.show_all_appointments()
                
                # Display next complete appointment if available
                if self.current_complete_petite_appointment_index < len(self.petite_complete_appointments):
                    self.display_petite_complete_appointment(self.current_complete_petite_appointment_index)
                elif self.current_complete_petite_appointment_index > 0:
                    self.current_complete_petite_appointment_index -= 1
                    self.display_petite_complete_appointment(self.current_complete_petite_appointment_index)
                else:
                    self.apppetite_complete_client_label.clear()
                    self.apppetite_complete_datetime_label.clear()
                    QMessageBox.warning(self, "Warning", "No more complete appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error undoing appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def show_classic_pending_appointments(self):
        self.stackedWidget.setCurrentIndex(8)
        self.classic_pending_appointments = self.fetch_classic_pending_appointments()
        self.current_pending_classic_appointment_index = 0 
        self.display_classic_pending_appointment(self.current_pending_classic_appointment_index)

    def fetch_classic_pending_appointments(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor() 
            cur.execute("SELECT * FROM APPOINTMENT WHERE app_status IN ('Pending', 'Rescheduled') AND app_package = 'Classic'")
            return cur.fetchall()
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error loading classic pending appointments: " + str(e))
            return []
        finally:
            if conn:
                cur.close()
                conn.close()

    def display_classic_pending_appointment(self, index):
        if index < len(self.classic_pending_appointments):
            appointment = self.classic_pending_appointments[index]
            client_code = appointment[1]  
            client_fname, client_lname = self.fetch_client_details(client_code)

            if client_fname and client_lname:
                self.appclassic_pending_client_label.setText(f"{client_fname} {client_lname}")
            else:
                self.appclassic_pending_client_label.setText("Unknown Client")
                
            self.appclassic_pending_datetime_label.setText(f"{appointment[2]}  {appointment[3]}")
        else:
            QMessageBox.warning(self, "Warning", "No more pending appointments to display.")

    def next_classic_pending_appointment(self): 
        self.current_pending_classic_appointment_index += 1
        self.display_classic_pending_appointment(self.current_pending_classic_appointment_index)

    def prev_classic_pending_appointment(self):
        if self.current_pending_classic_appointment_index > 0:
            self.current_pending_classic_appointment_index -= 1
            self.display_classic_pending_appointment(self.current_pending_classic_appointment_index)
        else:
            QMessageBox.warning(self, "Warning", "This is the first pending appointment.")

    def cancel_classic_pending_appointment(self): 
        confirmation = QMessageBox.question(self, "Cancel Appointment", "Are you sure you want to cancel this appointment?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            appointment = self.classic_pending_appointments[self.current_pending_classic_appointment_index]  # Get the current pending appointment
            
            # Update the status to 'Cancelled' in the database
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor() 
                cur.execute("UPDATE APPOINTMENT SET app_status = 'Cancelled' WHERE app_num = %s", (appointment[0],))
                conn.commit()
                QMessageBox.information(self, "Cancellation", "Appointment Cancelled Successfully")
                
                self.classic_pending_appointments.pop(self.current_pending_classic_appointment_index)  # Remove the cancelled appointment from the list
                
                self.update_pending_labels()
                self.show_all_appointments()
                
                # Display next pending appointment if available
                if self.current_pending_classic_appointment_index < len(self.classic_pending_appointments):
                    self.display_classic_pending_appointment(self.current_pending_classic_appointment_index)
                elif self.current_pending_classic_appointment_index > 0:
                    self.current_pending_classic_appointment_index -= 1
                    self.display_classic_pending_appointment(self.current_pending_classic_appointment_index)
                else:
                    self.appclassic_pending_client_label.clear()
                    self.appclassic_pending_datetime_label.clear()
                    QMessageBox.warning(self, "Warning", "No more pending appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error cancelling appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def noshow_classic_pending_appointment(self): 
        confirmation = QMessageBox.question(self, "Appointment No Show", "Are you sure you want to mark this appointment as 'No Show'?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            appointment = self.classic_pending_appointments[self.current_pending_classic_appointment_index]  # Get the current pending appointment
            
            # Update the status to 'Cancelled' in the database
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor() 
                cur.execute("UPDATE APPOINTMENT SET app_status = 'No Show' WHERE app_num = %s", (appointment[0],))
                conn.commit()
                QMessageBox.information(self, "No Show", "The appointment has been successfully marked as 'No Show'.")
                
                self.classic_pending_appointments.pop(self.current_pending_classic_appointment_index)  # Remove the no show appointment from the list
                
                self.update_pending_labels()
                self.show_all_appointments()
                
                # Display next pending appointment if available
                if self.current_pending_classic_appointment_index < len(self.classic_pending_appointments):
                    self.display_classic_pending_appointment(self.current_pending_classic_appointment_index)
                elif self.current_pending_classic_appointment_index > 0:
                    self.current_pending_classic_appointment_index -= 1
                    self.display_classic_pending_appointment(self.current_pending_classic_appointment_index)
                else:
                    self.appclassic_pending_client_label.clear()
                    self.appclassic_pending_datetime_label.clear()
                    QMessageBox.warning(self, "Warning", "No more pending appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error cancelling appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def resched_classic_pending_appointment(self): 
        self.stackedWidget.setCurrentIndex(9)

        # Retrieve current pending appointment
        if self.current_pending_classic_appointment_index < len(self.classic_pending_appointments):
            appointment = self.classic_pending_appointments[self.current_pending_classic_appointment_index]
            client_code = appointment[1]
            client_fname, client_lname = self.fetch_client_details(client_code)

            if client_fname and client_lname:
                self.appclassic_resched_client_label.setText(f"{client_fname} {client_lname}")
            else:
                self.appclassic_resched_client_label.setText("Unknown Client")
            self.appclassic_resched_origdatetime.setText(f"{appointment[2]}  {appointment[3]}")

            current_datetime = QDateTime.currentDateTime()
            self.appclassic_resched_datetime.setDateTime(current_datetime)
                
        else:
            QMessageBox.warning(self, "Warning", "No pending appointment to reschedule.")

    def classic_reschedule_save_button_clicked(self): 
        confirmation = QMessageBox.question(self, "Confirmation", "Are you sure you want to save changes?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            # Retrieve current pending appointment 
            if self.current_pending_classic_appointment_index < len(self.classic_pending_appointments):
                appointment = self.classic_pending_appointments[self.current_pending_classic_appointment_index]
                new_datetime = self.appclassic_resched_datetime.dateTime()
                new_date = new_datetime.toString("yyyy-MM-dd")
                new_start_time = new_datetime.toString("h:mm AP")  # Format time as 12-hour with AM/PM
                new_end_time = new_datetime.addSecs(30 * 60).toString("h:mm AP")  # End time
                new_time_range = f"{new_start_time} - {new_end_time}"
                # Update the database with new date and time
                conn = None
                try:
                    conn = self.create_database_connection()
                    cur = conn.cursor()
                    cur.execute("UPDATE APPOINTMENT SET app_date = %s, app_time = %s, app_status = 'Rescheduled' WHERE app_num = %s",
                                (new_date, new_time_range, appointment[0]))
                    conn.commit()
                    QMessageBox.information(self, "Success", "Appointment rescheduled successfully.")

                    self.show_all_appointments()
                    self.show_classic_pending_appointments()

                except psycopg2.Error as e:
                    QMessageBox.critical(self, "Database Error", "Error updating appointment: " + str(e))
                finally:
                    if conn:
                        cur.close()
                        conn.close()
            else:
                QMessageBox.warning(self, "Warning", "No pending appointment to reschedule.")

    def complete_classic_pending_appointment(self): 
        confirmation = QMessageBox.question(self, "Appointment Complete", "Are you sure you want to mark this appointment as 'Complete'?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            appointment = self.classic_pending_appointments[self.current_pending_classic_appointment_index]  # Get the current pending appointment
            
            # Update the status to 'Complete' in the database
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor() 
                cur.execute("UPDATE APPOINTMENT SET app_status = 'Complete' WHERE app_num = %s", (appointment[0],))
                conn.commit()
                QMessageBox.information(self, "Complete", "The appointment has been successfully marked as 'Complete'.")
                
                self.classic_pending_appointments.pop(self.current_pending_classic_appointment_index)  # Remove the completed appointment from the list
                
                self.update_pending_labels()
                self.show_all_appointments()
                
                # Display next pending appointment if available
                if self.current_pending_classic_appointment_index < len(self.classic_pending_appointments):
                    self.display_classic_pending_appointment(self.current_pending_classic_appointment_index)
                elif self.current_pending_classic_appointment_index > 0:
                    self.current_pending_classic_appointment_index -= 1
                    self.display_classic_pending_appointment(self.current_pending_classic_appointment_index)
                else:
                    self.appclassic_pending_client_label.clear()
                    self.appclassic_pending_datetime_label.clear()
                    QMessageBox.warning(self, "Warning", "No more pending appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error cancelling appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def show_classic_complete_appointments(self): 
        self.stackedWidget.setCurrentIndex(11)
        self.classic_complete_appointments = self.fetch_classic_complete_appointments()
        self.current_complete_classic_appointment_index = 0
        self.display_classic_complete_appointment(self.current_complete_classic_appointment_index)

    def fetch_classic_complete_appointments(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor() 
            cur.execute("SELECT * FROM APPOINTMENT WHERE app_status = 'Complete' AND app_package = 'Classic'")
            return cur.fetchall()
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error loading petite complete appointments: " + str(e))
            return []
        finally:
            if conn:
                cur.close()
                conn.close()

    def display_classic_complete_appointment(self, index):
        if index < len(self.classic_complete_appointments):
            appointment = self.classic_complete_appointments[index]
            client_code = appointment[1]  
            client_fname, client_lname = self.fetch_client_details(client_code)

            if client_fname and client_lname:
                self.appclassic_complete_client_label.setText(f"{client_fname} {client_lname}")
            else:
                self.appclassic_complete_client_label.setText("Unknown Client")
                
            self.appclassic_complete_datetime_label.setText(f"{appointment[2]}  {appointment[3]}")
        else:
            QMessageBox.warning(self, "Warning", "No more complete appointments to display.")

    def next_classic_complete_appointment(self): 
        self.current_complete_classic_appointment_index += 1
        self.display_classic_complete_appointment(self.current_complete_classic_appointment_index)

    def prev_classic_complete_appointment(self):
        if self.current_complete_classic_appointment_index > 0:
            self.current_complete_classic_appointment_index -= 1
            self.display_classic_complete_appointment(self.current_complete_classic_appointment_index)
        else:
            QMessageBox.warning(self, "Warning", "This is the first complete appointment.")

    def undo_classic_complete_appointment(self):
        confirmation = QMessageBox.question(self, "Confirmation", "Are you sure you want to undo the complete appointment?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            appointment = self.classic_complete_appointments[self.current_complete_classic_appointment_index]  # Get the current complete appointment
            
            # Update the status to 'Pending' in the database
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor() 
                cur.execute("UPDATE APPOINTMENT SET app_status = 'Pending' WHERE app_num = %s", (appointment[0],))
                conn.commit()
                QMessageBox.information(self, "Success", "Appointment successfully undone.")
                
                self.classic_complete_appointments.pop(self.current_complete_classic_appointment_index)  # Remove the undone appointment from the list
                
                self.update_pending_labels()
                self.show_all_appointments()
                
                # Display next complete appointment if available
                if self.current_complete_classic_appointment_index < len(self.classic_complete_appointments):
                    self.display_classic_complete_appointment(self.current_complete_classic_appointment_index)
                elif self.current_complete_classic_appointment_index > 0:
                    self.current_complete_classic_appointment_index -= 1
                    self.display_classic_complete_appointment(self.current_complete_classic_appointment_index)
                else:
                    self.appclassic_complete_client_label.clear()
                    self.appclassic_complete_datetime_label.clear()
                    QMessageBox.warning(self, "Warning", "No more complete appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error undoing appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def search_appointments(self):
        search_app = self.search_app.text().strip().lower()
        if not search_app:
            return

        for row in range(self.appTable.rowCount()):
            row_text = " ".join([self.appTable.item(row, col).text().lower() for col in range(self.appTable.columnCount())])
            if search_app in row_text:
                self.appTable.setRowHidden(row, False)
            else:
                self.appTable.setRowHidden(row, True)

    def reset_appointments_table(self):
        for row in range(self.appTable.rowCount()):
            self.appTable.setRowHidden(row, False)

    def delete_app(self):
        selected_row = self.appTable.currentRow()
        if selected_row != -1:
            confirmation = QMessageBox.question(self, "Delete Appointment", "Are you sure you want to delete this appointment?", QMessageBox.Yes | QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                try:
                    conn = self.create_database_connection()
                    cur = conn.cursor()

                    # Get the appointment number from the selected row
                    app_num_item = self.appTable.item(selected_row, 0)
                    if app_num_item is not None:
                        app_num = app_num_item.text()

                        cur.execute("DELETE FROM APPOINTMENT WHERE APP_NUM = %s", (app_num,))

                        # Commit the transaction
                        conn.commit()

                        self.appTable.removeRow(selected_row)
                        QMessageBox.information(self, "Delete Appointment", "Appointment deleted successfully.")
                        # Update the appointment table
                        self.show_all_appointments()
                        self.update_pending_labels()
                        self.display_total_appointments()

                    else:
                        QMessageBox.warning(self, "Delete Appointment", "Selected row does not contain appointment information.")

                except psycopg2.Error as e:
                    QMessageBox.critical(self, "Database Error", "Error deleting appointment from the database: " + str(e))
                finally:
                    if conn:
                        cur.close()
                        conn.close()

            else:
                QMessageBox.warning(self, "Delete Appointment", "Deletion canceled.")
        else:
            QMessageBox.warning(self, "Delete Appointment", "Select a row in the appointment table to delete.")

    def send_email_for_appointment(self):
        # Check if a row is selected
        selected_row = self.appTable.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Send Email", "Please select a row in the appointment table to send the email.")
            return

        # Get appointment details from the selected row
        client_email = self.appTable.item(selected_row, 2).text() 
        status = self.appTable.item(selected_row, 7).text()  
        package = self.appTable.item(selected_row, 3).text()  
        date = self.appTable.item(selected_row, 4).text()  
        time = self.appTable.item(selected_row, 5).text()  
        address = self.appTable.item(selected_row, 6).text()  

        # Check if client's email is available
        if not client_email:
            QMessageBox.warning(self, "Send Email", "Client's email not found.")
            return
        
        # Get reasons from QTextEdits
        if status == "Rescheduled":
            if package == "Classic":
                reasons = self.appclassic_resched_reason.toPlainText()
            elif package == "Petite":
                reasons = self.apppetite_resched_reason.toPlainText()

        # Construct email message based on appointment status
        if status == "Cancelled":
            subject = "Appointment Cancelled"
            body = f"""Dear Customer,

Your appointment for {package} on {date} at {time} has been cancelled.
Location: {address}
Reasons:

Please contact us for rescheduling or any queries.

Regards,
Uclick Self-Portrait Studio"""
        elif status == "No Show":
            subject = "Appointment No Show"
            body = f"""Dear Customer,

We missed you at your appointment for {package} on {date} at {time}.
Location: {address}

Please contact us if you need to reschedule or have any questions.

Regards,
Uclick Self-Portrait Studio"""
        elif status == "Rescheduled":
            subject = "Appointment Rescheduled"
            body = f"""Dear Customer,

Your appointment for {package} has been rescheduled on {date} at {time}.
Location: {address}
Reasons:
{reasons}

Please note the new date and time.

Regards,
Uclick Self-Portrait Studio"""
        elif status == "Complete":
            subject = "Appointment Completed"
            body = f"""Dear Customer,

Your appointment for {package} on {date} at {time} has been completed.
Location: {address}

We hope to see you again soon!

Regards,
Uclick Self-Portrait Studio"""

        # Construct the URL for composing the email in Gmail
        url = "https://mail.google.com/mail/?view=cm&to={}&su={}&body={}".format(
            quote(client_email), quote(subject), quote(body)
        )

        webbrowser.open(url)

    def show_clients(self):
        self.stackedWidget.setCurrentIndex(12)
        self.current_index = 2
        self.clients_button.setChecked(True)
        self.previous_button_index = 2
        self.load_clients_data()

    def load_clients_data(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor()

            query = """
                SELECT
                    CLIENT.client_code,
                    client_fname,
                    client_lname,
                    client_email,
                    client_contact_number,
                    COUNT(APPOINTMENT.client_code) AS num_apps
                FROM
                    CLIENT
                LEFT JOIN
                    APPOINTMENT ON CLIENT.client_code = APPOINTMENT.client_code
                GROUP BY
                    CLIENT.client_code,
                    client_fname,
                    client_lname,
                    client_email,
                    client_contact_number
                ORDER BY
                    client_fname ASC,
                    client_lname ASC
            """

            cur.execute(query)
            clients = cur.fetchall()

            self.client_list.setRowCount(len(clients))
            self.client_list.setColumnCount(6)
            column_names = ['Client Code', 'First Name', 'Last Name', 'Email Address', 'Contact Number', 'No. of Appointments']
            self.client_list.setHorizontalHeaderLabels(column_names)
            font = QFont()
            font.setBold(True)
            font.setPointSize(12)
            self.client_list.horizontalHeader().setFont(font)
            for i, row in enumerate(clients):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.client_list.setItem(i, j, item)

            # Resize columns to fit contents
            self.client_list.resizeColumnsToContents()
            self.client_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.stackedWidget.setCurrentIndex(12) 

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error loading active client data: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def archive_client(self):
        selected_row = self.client_list.currentRow()
        if selected_row == -1:  # If no row is selected
            QMessageBox.warning(self, "Warning", "Please select a client to archive.")
            return

        client_code = self.client_list.item(selected_row, 0).text()
        client_name = self.client_list.item(selected_row, 1).text() + " " + self.client_list.item(selected_row, 2).text()

        # Ask for confirmation
        confirmation = QMessageBox.question(self, "Confirmation", f"Are you sure you want to archive the client '{client_name}'?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.No:
            return

        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor()

            # Begin transaction
            conn.autocommit = False

            # Move client data to CLIENT_ARCHIVE
            cur.execute("""
                INSERT INTO CLIENT_ARCHIVE (client_code, client_fname, client_lname, client_contact_number, client_email)
                SELECT client_code, client_fname, client_lname, client_contact_number, client_email
                FROM CLIENT
                WHERE client_code = %s
            """, (client_code,))

            # Move client's appointments to APPOINTMENT_ARCHIVE
            cur.execute("""
                INSERT INTO APPOINTMENT_ARCHIVE (app_num, client_code, app_date, app_time, app_address, app_status, app_package, emp_code)
                SELECT app_num, client_code, app_date, app_time, app_address, app_status, app_package, emp_code
                FROM APPOINTMENT
                WHERE client_code = %s
            """, (client_code,))

            # Move client's bills to BILL_ARCHIVE
            cur.execute("""
                INSERT INTO BILL_ARCHIVE (bill_num, bill_session_date, bill_package, bill_add_services, bill_amount_due, bill_amount_paid, bill_mode, client_code, emp_code, app_num)
                SELECT bill_num, bill_session_date, bill_package, bill_add_services, bill_amount_due, bill_amount_paid, bill_mode, client_code, emp_code, app_num
                FROM BILL
                WHERE client_code = %s
            """, (client_code,))

            # Delete client from CLIENT table
            cur.execute("DELETE FROM CLIENT WHERE client_code = %s", (client_code,))

            # Delete client's appointments from APPOINTMENT table
            cur.execute("DELETE FROM APPOINTMENT WHERE client_code = %s", (client_code,))

            # Delete client's bills from BILL table
            cur.execute("DELETE FROM BILL WHERE client_code = %s", (client_code,))

            # Commit transaction
            conn.commit()
            QMessageBox.information(self, "Success", "Client archived successfully.")

            # Reload the client list
            self.load_clients_data()
            # Update the labels
            self.update_pending_labels()
            self.display_total_appointments()
            self.display_total_clients()
            self.display_total_bills()

        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            QMessageBox.critical(self, "Database Error", "Error archiving client: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def search_clients(self):
        search_for_clients = self.search_client.text().strip().lower()
        if not search_for_clients:
            return

        for row in range(self.client_list.rowCount()):
            row_text = " ".join([self.client_list.item(row, col).text().lower() for col in range(self.client_list.columnCount())])
            if search_for_clients in row_text:
                self.client_list.setRowHidden(row, False)
            else:
                self.client_list.setRowHidden(row, True)

    def reset_clients_table(self):
        for row in range(self.client_list.rowCount()):
            self.client_list.setRowHidden(row, False)

    def view_client_info(self):
        # Get selected row
        selected_row = self.client_list.currentRow()
        if selected_row != -1:  # If a row is selected
            self.stackedWidget.setCurrentIndex(14)
            self.current_client_info_index = selected_row
            self.display_client_info(selected_row)
        else:
            QMessageBox.warning(self, "Warning", "Please select a client to view.")

    def display_client_info(self, index):
        if index >= 0 and index < self.client_list.rowCount():
            client_fname = self.client_list.item(index, 1).text()
            client_lname = self.client_list.item(index, 2).text()
            client_email = self.client_list.item(index, 3).text()
            client_contact = self.client_list.item(index, 4).text()
                
            self.client_info_fname.setText(f"{client_fname}")
            self.client_info_lname.setText(f"{client_lname}")
            self.client_info_email.setText(f"{client_email}")
            self.client_info_contact.setText(f"{client_contact}")
                    
        else:
            QMessageBox.warning(self, "Warning", "No more client information to display.")

    def next_client_info(self): 
        self.current_client_info_index += 1
        self.display_client_info(self.current_client_info_index)

    def prev_client_info(self):
        if self.current_client_info_index > 0:
            self.current_client_info_index -= 1
            self.display_client_info(self.current_client_info_index)
        else:
            QMessageBox.warning(self, "Warning", "This is the first client in the list.")

    def edit_client_info(self):
        selected_row = self.client_list.currentRow()
        if selected_row != -1:  # If a row is selected
            # Retrieve data from selected row
            client_code = self.client_list.item(selected_row, 0).text()  # Assuming client_code is in the first column
            client_fname = self.client_list.item(selected_row, 1).text()
            client_lname = self.client_list.item(selected_row, 2).text()
            client_email = self.client_list.item(selected_row, 3).text()
            client_contact = self.client_list.item(selected_row, 4).text()

            # Set data into line edits
            self.client_editinfo_fname.setText(client_fname)
            self.client_editinfo_lname.setText(client_lname)
            self.client_editinfo_email.setText(client_email)
            self.client_editinfo_contact.setText(client_contact)

            # Store client_code for later use in save_changes
            self.current_editing_client_code = client_code  # Store client_code attribute in the instance

            # Switch to the edit page
            self.stackedWidget.setCurrentIndex(13)
        else:
            QMessageBox.warning(self, "Warning", "Please select a client to edit.")

    def confirm_save_changes(self):
        confirmation = QMessageBox.question(self, "Confirmation", "Are you sure you want to save the changes?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            self.save_changes()

    def save_changes(self):
        selected_row = self.client_list.currentRow()
        if selected_row != -1:  # If a row is selected
            # Retrieve original data from the selected row in the client list table
            original_fname = self.client_list.item(selected_row, 1).text()
            original_lname = self.client_list.item(selected_row, 2).text()
            original_email = self.client_list.item(selected_row, 3).text()
            original_contact = self.client_list.item(selected_row, 4).text()

            # Use the stored client_code from editing
            client_code = self.current_editing_client_code

            if client_code:
                # Retrieve data from line edits
                edited_fname = self.client_editinfo_fname.text()
                edited_lname = self.client_editinfo_lname.text()
                edited_email = self.client_editinfo_email.text()
                edited_contact = self.client_editinfo_contact.text()

                # Update the selected row in the client list table
                self.client_list.item(selected_row, 1).setText(edited_fname)
                self.client_list.item(selected_row, 2).setText(edited_lname)
                self.client_list.item(selected_row, 3).setText(edited_email)
                self.client_list.item(selected_row, 4).setText(edited_contact)

                # Update the client table in the database
                conn = None
                try:
                    conn = self.create_database_connection()
                    cur = conn.cursor()

                    cur.execute("UPDATE CLIENT SET client_fname = %s, client_lname = %s, client_email = %s, client_contact_number = %s WHERE client_code = %s",
                                (edited_fname, edited_lname, edited_email, edited_contact, client_code))
                    conn.commit()
                    QMessageBox.information(self, "Success", "Changes saved successfully.")
                    self.show_clients()
                except psycopg2.Error as e:
                    QMessageBox.critical(self, "Database Error", "Error updating client data: " + str(e))
                finally:
                    if conn:
                        cur.close()
                        conn.close()
            else:
                QMessageBox.warning(self, "Warning", "Client code not found for the selected client.")
        else:
            QMessageBox.warning(self, "Warning", "Please select a client to edit.")

    def client_appointment_history(self):
        selected_row = self.client_list.currentRow()
        if selected_row != -1:  # If a row is selected
            # Retrieve original data from the selected row in the client list table
            client_code = self.client_list.item(selected_row, 0).text()  # Adjust index to 0 for client_code
            original_fname = self.client_list.item(selected_row, 1).text()  # Adjust index accordingly
            original_lname = self.client_list.item(selected_row, 2).text()  # Adjust index accordingly
            original_email = self.client_list.item(selected_row, 3).text()  # Adjust index accordingly
            original_contact = self.client_list.item(selected_row, 4).text()  # Adjust index accordingly

            self.client_apphist.setText(f"Client: {original_fname} {original_lname}")

            # Fetch appointment history from database using client_code
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor()

                # Select appointments and bills for the given client code, ordered by date and time descending
                cur.execute("""
                    SELECT a.app_date, a.app_time, a.app_package, b.bill_add_services, b.bill_amount_due, b.bill_mode, a.app_status 
                    FROM appointment AS a 
                    LEFT JOIN bill AS b ON a.app_num = b.app_num 
                    WHERE a.client_code = %s
                    ORDER BY a.app_date DESC, a.app_time DESC
                """, (client_code,))
                appointment_history = cur.fetchall()

                # Populate the client_app_history_table
                self.client_app_history_table.setRowCount(len(appointment_history))
                self.client_app_history_table.setColumnCount(7)
                column_names = ['Date', 'Time', 'Package', 'Additional Services', 'Amount Due', 'Payment Mode', 'Status']
                self.client_app_history_table.setHorizontalHeaderLabels(column_names)
                font = QFont()
                font.setBold(True)
                font.setPointSize(12) 
                self.client_app_history_table.horizontalHeader().setFont(font)

                for i, (date, time, package, additional_services, amount_due, payment_mode, status) in enumerate(appointment_history):
                    item_date = QTableWidgetItem(str(date))
                    item_time = QTableWidgetItem(str(time))
                    item_package = QTableWidgetItem(str(package))
                    item_additional_services = QTableWidgetItem(str(additional_services))
                    item_amount_due = QTableWidgetItem(str(amount_due))
                    item_payment_mode = QTableWidgetItem(str(payment_mode))
                    item_status = QTableWidgetItem(str(status))

                    self.client_app_history_table.setItem(i, 0, item_date)
                    self.client_app_history_table.setItem(i, 1, item_time)
                    self.client_app_history_table.setItem(i, 2, item_package)
                    self.client_app_history_table.setItem(i, 3, item_additional_services)
                    self.client_app_history_table.setItem(i, 4, item_amount_due)
                    self.client_app_history_table.setItem(i, 5, item_payment_mode)
                    self.client_app_history_table.setItem(i, 6, item_status)

                # Resize columns to fit contents
                self.client_app_history_table.resizeColumnsToContents()
                self.client_app_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

                self.stackedWidget.setCurrentIndex(15)  # Switch to the appointment history page
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error fetching appointment history: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()
        else:
            QMessageBox.warning(self, "Warning", "Please select a client to view appointment history.")

    def search_client_app_hist(self):
        app_hist = self.search_apphist.text().strip().lower()
        if not app_hist:
            return

        for row in range(self.client_app_history_table.rowCount()):
            row_text = " ".join([self.client_app_history_table.item(row, col).text().lower() for col in range(self.client_app_history_table.columnCount())])
            if app_hist in row_text:
                self.client_app_history_table.setRowHidden(row, False)
            else:
                self.client_app_history_table.setRowHidden(row, True)

    def reset_apphist_table(self):
        for row in range(self.client_app_history_table.rowCount()):
            self.client_app_history_table.setRowHidden(row, False)

    def load_archived_clients(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor()

            query = """
                SELECT
                    CLIENT_ARCHIVE.client_code,
                    client_fname,
                    client_lname,
                    client_email,
                    client_contact_number,
                    COUNT(APPOINTMENT_ARCHIVE.client_code) AS num_apps
                FROM
                    CLIENT_ARCHIVE
                LEFT JOIN
                    APPOINTMENT_ARCHIVE ON CLIENT_ARCHIVE.client_code = APPOINTMENT_ARCHIVE.client_code
                GROUP BY
                    CLIENT_ARCHIVE.client_code,
                    client_fname,
                    client_lname,
                    client_email,
                    client_contact_number
                ORDER BY
                    client_fname ASC,
                    client_lname ASC
            """

            cur.execute(query)
            clients = cur.fetchall()

            self.archived_client_list.setRowCount(len(clients))
            self.archived_client_list.setColumnCount(6)
            column_names = ['Client Code', 'First Name', 'Last Name', 'Email Address', 'Contact Number', 'No. of Appointments']
            self.archived_client_list.setHorizontalHeaderLabels(column_names)
            font = QFont()
            font.setBold(True)
            font.setPointSize(12)
            self.archived_client_list.horizontalHeader().setFont(font)
            for i, row in enumerate(clients):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.archived_client_list.setItem(i, j, item)

            # Resize columns to fit contents
            self.archived_client_list.resizeColumnsToContents()
            self.archived_client_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)       
            self.stackedWidget.setCurrentIndex(16)  # Switch to the archived client view

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error loading archived client data: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def restore_client(self):
        selected_row = self.archived_client_list.currentRow()  # Use archived_client_list
        if selected_row == -1:  # If no row is selected
            QMessageBox.warning(self, "Warning", "Please select a client to restore.")
            return

        client_code = self.archived_client_list.item(selected_row, 0).text()
        client_name = self.archived_client_list.item(selected_row, 1).text() + " " + self.archived_client_list.item(selected_row, 2).text()

        # Ask for confirmation
        confirmation = QMessageBox.question(self, "Confirmation", f"Are you sure you want to restore the client '{client_name}'?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.No:
            return

        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor()

            # Begin transaction
            conn.autocommit = False

            # Move client data back to CLIENT
            cur.execute("""
                INSERT INTO CLIENT (client_code, client_fname, client_lname, client_contact_number, client_email)
                SELECT client_code, client_fname, client_lname, client_contact_number, client_email
                FROM CLIENT_ARCHIVE
                WHERE client_code = %s
            """, (client_code,))

            # Move client's appointments back to APPOINTMENT
            cur.execute("""
                INSERT INTO APPOINTMENT (app_num, client_code, app_date, app_time, app_address, app_status, app_package, emp_code)
                SELECT app_num, client_code, app_date, app_time, app_address, app_status, app_package, emp_code
                FROM APPOINTMENT_ARCHIVE
                WHERE client_code = %s
            """, (client_code,))

            # Move client's bills back to BILL
            cur.execute("""
                INSERT INTO BILL (bill_num, bill_session_date, bill_package, bill_add_services, bill_amount_due, bill_amount_paid, bill_mode, client_code, emp_code, app_num)
                SELECT bill_num, bill_session_date, bill_package, bill_add_services, bill_amount_due, bill_amount_paid, bill_mode, client_code, emp_code, app_num
                FROM BILL_ARCHIVE
                WHERE client_code = %s
            """, (client_code,))

            # Delete client from CLIENT_ARCHIVE table
            cur.execute("DELETE FROM CLIENT_ARCHIVE WHERE client_code = %s", (client_code,))

            # Delete client's appointments from APPOINTMENT_ARCHIVE table
            cur.execute("DELETE FROM APPOINTMENT_ARCHIVE WHERE client_code = %s", (client_code,))

            # Delete client's bills from BILL_ARCHIVE table
            cur.execute("DELETE FROM BILL_ARCHIVE WHERE client_code = %s", (client_code,))

            # Commit transaction
            conn.commit()
            QMessageBox.information(self, "Success", "Client restored successfully.")

            # Reload the archived client list
            self.load_archived_clients()
            # Update the labels
            self.update_pending_labels()
            self.display_total_appointments()
            self.display_total_clients()
            self.display_total_bills()

        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            QMessageBox.critical(self, "Database Error", "Error restoring client: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def search_archived_clients(self):
        search_for_archived_clients = self.search_archived_client.text().strip().lower()
        if not search_for_archived_clients:
            return

        for row in range(self.archived_client_list.rowCount()):
            row_text = " ".join([
                self.archived_client_list.item(row, col).text().lower() if self.archived_client_list.item(row, col) is not None else ""
                for col in range(self.archived_client_list.columnCount())
            ])
            if search_for_archived_clients in row_text:
                self.archived_client_list.setRowHidden(row, False)
            else:
                self.archived_client_list.setRowHidden(row, True)

    def reset_archived_clients_table(self):
        for row in range(self.archived_client_list.rowCount()):
            self.archived_client_list.setRowHidden(row, False)

    def view_archived_client_info(self):
        # Get selected row
        selected_row = self.archived_client_list.currentRow()
        if selected_row != -1:  # If a row is selected
            self.stackedWidget.setCurrentIndex(18)
            self.current_archived_client_info_index = selected_row
            self.display_archived_client_info(selected_row)
        else:
            QMessageBox.warning(self, "Warning", "Please select an archived client to view.")

    def display_archived_client_info(self, index):
        if index >= 0 and index < self.archived_client_list.rowCount():
            archived_client_fname = self.archived_client_list.item(index, 1).text()
            archived_client_lname = self.archived_client_list.item(index, 2).text()
            archived_client_email = self.archived_client_list.item(index, 3).text()
            archived_client_contact = self.archived_client_list.item(index, 4).text()
                
            self.archived_client_info_fname.setText(f"{archived_client_fname}")
            self.archived_client_info_lname.setText(f"{archived_client_lname}")
            self.archived_client_info_email.setText(f"{archived_client_email}")
            self.archived_client_info_contact.setText(f"{archived_client_contact}")
                    
        else:
            QMessageBox.warning(self, "Warning", "No more archived client information to display.")

    def next_archived_client_info(self): 
        self.current_archived_client_info_index += 1
        self.display_archived_client_info(self.current_archived_client_info_index)

    def prev_archived_client_info(self):
        if self.current_archived_client_info_index > 0:
            self.current_archived_client_info_index -= 1
            self.display_archived_client_info(self.current_archived_client_info_index)
        else:
            QMessageBox.warning(self, "Warning", "This is the first archived client in the list.")

    def archived_client_appointment_history(self):
        selected_row = self.archived_client_list.currentRow()
        if selected_row != -1:  # If a row is selected
            # Retrieve original data from the selected row in the client list table
            archived_client_code = self.archived_client_list.item(selected_row, 0).text()  # Adjust index to 0 for client_code
            archived_original_fname = self.archived_client_list.item(selected_row, 1).text()  # Adjust index accordingly
            archived_original_lname = self.archived_client_list.item(selected_row, 2).text()  # Adjust index accordingly
            archived_original_email = self.archived_client_list.item(selected_row, 3).text()  # Adjust index accordingly
            archived_original_contact = self.archived_client_list.item(selected_row, 4).text()  # Adjust index accordingly

            self.archived_client_apphist.setText(f"Client: {archived_original_fname} {archived_original_lname}")

            # Fetch appointment history from database using client_code
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor()

                # Select appointments and bills for the given client code, ordered by date and time descending
                cur.execute("""
                    SELECT a.app_date, a.app_time, a.app_package, b.bill_add_services, b.bill_amount_due, b.bill_mode, a.app_status 
                    FROM appointment_archive AS a 
                    LEFT JOIN bill_archive AS b ON a.app_num = b.app_num 
                    WHERE a.client_code = %s
                    ORDER BY a.app_date DESC, a.app_time DESC
                """, (archived_client_code,))
                archived_appointment_history = cur.fetchall()

                # Populate the archived_client_app_history_table
                self.archived_client_app_history_table.setRowCount(len(archived_appointment_history))
                self.archived_client_app_history_table.setColumnCount(7)
                column_names = ['Date', 'Time', 'Package', 'Additional Services', 'Amount Due', 'Payment Mode', 'Status']
                self.archived_client_app_history_table.setHorizontalHeaderLabels(column_names)
                font = QFont()
                font.setBold(True)
                font.setPointSize(12) 
                self.archived_client_app_history_table.horizontalHeader().setFont(font)

                for i, (date, time, package, additional_services, amount_due, payment_mode, status) in enumerate(archived_appointment_history):
                    item_date = QTableWidgetItem(str(date))
                    item_time = QTableWidgetItem(str(time))
                    item_package = QTableWidgetItem(str(package))
                    item_additional_services = QTableWidgetItem(str(additional_services))
                    item_amount_due = QTableWidgetItem(str(amount_due))
                    item_payment_mode = QTableWidgetItem(str(payment_mode))
                    item_status = QTableWidgetItem(str(status))

                    self.archived_client_app_history_table.setItem(i, 0, item_date)
                    self.archived_client_app_history_table.setItem(i, 1, item_time)
                    self.archived_client_app_history_table.setItem(i, 2, item_package)
                    self.archived_client_app_history_table.setItem(i, 3, item_additional_services)
                    self.archived_client_app_history_table.setItem(i, 4, item_amount_due)
                    self.archived_client_app_history_table.setItem(i, 5, item_payment_mode)
                    self.archived_client_app_history_table.setItem(i, 6, item_status)

                # Resize columns to fit contents
                self.archived_client_app_history_table.resizeColumnsToContents()
                self.archived_client_app_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

                self.stackedWidget.setCurrentIndex(19)  # Switch to the appointment history page
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error fetching archived appointment history: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()
        else:
            QMessageBox.warning(self, "Warning", "Please select an archived client to view appointment history.")

    def search_archived_client_app_hist(self):
        archived_app_hist = self.search_archived_apphist.text().strip().lower()
        if not archived_app_hist:
            return

        for row in range(self.archived_client_app_history_table.rowCount()):
            row_text = " ".join([self.archived_client_app_history_table.item(row, col).text().lower() for col in range(self.archived_client_app_history_table.columnCount())])
            if archived_app_hist in row_text:
                self.archived_client_app_history_table.setRowHidden(row, False)
            else:
                self.archived_client_app_history_table.setRowHidden(row, True)

    def reset_archived_apphist_table(self):
        for row in range(self.archived_client_app_history_table.rowCount()):
            self.archived_client_app_history_table.setRowHidden(row, False)

    def show_billing(self):
        self.stackedWidget.setCurrentIndex(20)
        self.current_index = 3
        self.billing_button.setChecked(True)
        self.previous_button_index = 3
        self.load_billing_data()
        # Group radio buttons for the package
        package_group = QButtonGroup(self)
        package_group.addButton(self.radioButton_petite)
        package_group.addButton(self.radioButton_classic)
        # Group radio buttons for the mode
        mode_group = QButtonGroup(self)
        mode_group.addButton(self.radioButton_cash)
        mode_group.addButton(self.radioButton_gcash)

        # Connect signals to calculate the amount due
        package_group.buttonClicked.connect(self.calculate_amount_due)
        self.checkBox_1.stateChanged.connect(self.calculate_amount_due)
        self.checkBox_2.stateChanged.connect(self.calculate_amount_due)
        self.checkBox_3.stateChanged.connect(self.calculate_amount_due)
        self.checkBox_4.stateChanged.connect(self.calculate_amount_due)
        self.checkBox_5.stateChanged.connect(self.calculate_amount_due)
        self.checkBox_6.stateChanged.connect(self.calculate_amount_due)
        self.checkBox_7.stateChanged.connect(self.calculate_amount_due)
        self.amountpaid.textChanged.connect(self.calculate_change)
        
    def load_billing_data(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor() 
            cur.execute("""
                SELECT B.BILL_NUM, B.BILL_SESSION_DATE, B.BILL_PACKAGE, B.BILL_ADD_SERVICES, B.BILL_AMOUNT_DUE, 
                    B.BILL_AMOUNT_PAID, B.BILL_MODE, C.CLIENT_FNAME || ' ' || C.CLIENT_LNAME AS CLIENT_NAME, 
                    C.CLIENT_CONTACT_NUMBER, C.CLIENT_EMAIL, E.EMP_FNAME || ' ' || E.EMP_LNAME AS EMP_NAME 
                FROM BILL B 
                LEFT JOIN CLIENT C ON B.CLIENT_CODE = C.CLIENT_CODE
                LEFT JOIN EMPLOYEE E ON B.EMP_CODE = E.EMP_CODE
                ORDER BY B.BILL_SESSION_DATE DESC
            """)
            result = cur.fetchall() 

            self.bill_list.setRowCount(len(result))
            self.bill_list.setColumnCount(11) 
            column_names = ['Bill Number', 'Session Date', 'Package', 'Additional', 'Amount Due', 'Amount Paid', 'Mode', 'Client Name', 'Client Phone', 'Client Email', 'Issued by']
            self.bill_list.setHorizontalHeaderLabels(column_names)
            font = QFont()
            font.setBold(True)
            font.setPointSize(12) 
            self.bill_list.horizontalHeader().setFont(font)
            for i, row in enumerate(result):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.bill_list.setItem(i, j, item)

            # Resize columns to fit contents
            self.bill_list.resizeColumnsToContents()
            self.bill_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error loading billing data: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def search_bills(self):
        search_text = self.search.text().strip().lower()
        if not search_text:
            return

        for row in range(self.bill_list.rowCount()):
            row_text = " ".join([self.bill_list.item(row, col).text().lower() for col in range(self.bill_list.columnCount())])
            if search_text in row_text:
                self.bill_list.setRowHidden(row, False)
            else:
                self.bill_list.setRowHidden(row, True)

    def reset_bill_table(self):
        for row in range(self.bill_list.rowCount()):
            self.bill_list.setRowHidden(row, False)

    def calculate_amount_due(self):
        package_price = 0
        additional_services_price = 0

        # Calculate package price
        if self.radioButton_petite.isChecked():
            package_price = 600
        elif self.radioButton_classic.isChecked():
            package_price = 1200

        # Calculate additional services price
        if self.checkBox_1.isChecked() and self.checkBox_1_qty.text().strip():
            additional_services_price += 200 * int(self.checkBox_1_qty.text())
        if self.checkBox_2.isChecked() and self.checkBox_2_qty.text().strip():
            additional_services_price += 100 * int(self.checkBox_2_qty.text())
        if self.checkBox_3.isChecked() and self.checkBox_3_qty.text().strip():
            additional_services_price += 100 * int(self.checkBox_3_qty.text())
        if self.checkBox_4.isChecked() and self.checkBox_4_qty.text().strip():
            additional_services_price += 50 * int(self.checkBox_4_qty.text())
        if self.checkBox_5.isChecked():
            additional_services_price += 300
        if self.checkBox_6.isChecked():
            additional_services_price += 250
        if self.checkBox_7.isChecked() and self.checkBox_7_qty.text().strip():
            additional_services_price += 100 * int(self.checkBox_7_qty.text())

        # Calculate total amount due if at least one checkbox is checked with quantity
        if package_price > 0 or additional_services_price > 0:
            total_amount_due = package_price + additional_services_price
            self.amountdue.setText(str(total_amount_due))
        else:
            self.amountdue.setText("")

            # Calculate total amount due
        total_amount_due = package_price + additional_services_price

        # Display total amount due
        self.amountdue.setText(str(total_amount_due))

    def calculate_change(self):
        try:
            total_due = int(self.amountdue.text())
            amount_paid = int(self.amountpaid.text())
            change = amount_paid - total_due
            self.change.setText(str(change))
        except ValueError:
            self.change.setText("Invalid input")

    def generate_bill_num(self, client_fname, client_lname, emp_fname, emp_lname):
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{client_fname[0]}{client_lname[0]}{current_datetime}{emp_fname[0]}{emp_lname[0]}"

    def generate_bill(self):
        # Get/Check Billing Form values
        client_fname = self.fname.text().strip()
        client_lname = self.lname.text().strip()
        session_date_str = self.sess_date.text().strip()
        package = ""
        additional_services = ""
        if self.radioButton_petite.isChecked():
            package = 'Petite'
        elif self.radioButton_classic.isChecked():
            package = 'Classic'
        if any([checkbox.isChecked() for checkbox in [self.checkBox_1, self.checkBox_2, self.checkBox_3, self.checkBox_4, self.checkBox_5, self.checkBox_6, self.checkBox_7]]):
            additional_services = 'Yes'
        else:
            additional_services = 'No'
        amount_paid = self.amountpaid.text().strip()
        self.calculate_amount_due()
        self.calculate_change()
        mode = ""
        if self.radioButton_cash.isChecked():
            mode = "Cash"
        elif self.radioButton_gcash.isChecked():
            mode = "GCash"
        emp_fname = self.emp_fname.text().strip()
        emp_lname = self.emp_lname.text().strip()

        # Check/Validate inputs
        if not client_fname or not client_lname or not session_date_str or not amount_paid or not emp_fname or not emp_lname:
            QMessageBox.warning(self, "Generate Bill", "Please fill in all fields.")
            return
        
        try:
            session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date()
        except ValueError:
            QMessageBox.warning(self, "Generate Bill", "Please enter the session date in the format yyyy-mm-dd.")
            return

        # Check if package is selected
        if not self.radioButton_petite.isChecked() and not self.radioButton_classic.isChecked():
            QMessageBox.warning(self, "Generate Bill", "Please select a package.")
            return
        
        try:
            amount_paid = int(amount_paid)
        except ValueError:
            QMessageBox.warning(self, "Generate Bill", "Please enter a valid amount for 'Amount Paid'.")
            return

        # Check if mode is selected
        if not self.radioButton_cash.isChecked() and not self.radioButton_gcash.isChecked():
            QMessageBox.warning(self, "Generate Bill", "Please select a payment mode.")
            return

        try:
            conn = self.create_database_connection()
            cur = conn.cursor()

            cur.execute("SELECT CLIENT_CODE FROM CLIENT WHERE CLIENT_FNAME = %s AND CLIENT_LNAME = %s", (client_fname, client_lname))
            client_code = cur.fetchone()
            if not client_code:
                QMessageBox.warning(self, "Generate Bill", "Client not found.")
                return
            client_code = client_code[0]

            cur.execute("SELECT EMP_CODE FROM EMPLOYEE WHERE EMP_FNAME = %s AND EMP_LNAME = %s", (emp_fname, emp_lname))
            emp_code = cur.fetchone()
            if not emp_code:
                QMessageBox.warning(self, "Generate Bill", "Employee not found.")
                return
            emp_code = emp_code[0]

            # Retrieve app_num from APPOINTMENT table based on client, package, and session date
            cur.execute("SELECT APP_NUM FROM APPOINTMENT WHERE CLIENT_CODE = %s AND APP_PACKAGE = %s AND APP_DATE = %s", (client_code, package, session_date))
            app_num = cur.fetchone()
            if not app_num:
                QMessageBox.warning(self, "Generate Bill", "No appointment found for the specified client, package, and session date.")
                return
            app_num = app_num[0]

            # Check if the app_num already exists in the BILL table
            cur.execute("SELECT BILL_NUM FROM BILL WHERE APP_NUM = %s", (app_num,))
            existing_bill = cur.fetchone()
            if existing_bill:
                QMessageBox.warning(self, "Generate Bill", "A bill for this appointment already exists.")
                return

            bill_num = self.generate_bill_num(client_fname, client_lname, emp_fname, emp_lname)

            cur.execute("INSERT INTO BILL (BILL_NUM, BILL_SESSION_DATE, BILL_PACKAGE, BILL_ADD_SERVICES, BILL_AMOUNT_DUE, BILL_AMOUNT_PAID, BILL_MODE, CLIENT_CODE, EMP_CODE, APP_NUM) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (bill_num, session_date, package, additional_services, self.amountdue.text(), amount_paid, mode, client_code, emp_code, app_num))
            conn.commit()

            self.load_billing_data()
            self.display_total_bills()

            QMessageBox.information(self, "Generate Bill", "Bill generated successfully.")

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error generating bill: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def clear_fields(self):
        self.fname.clear()
        self.lname.clear()
        self.sess_date.clear()
        self.amountpaid.clear()
        self.emp_fname.clear()
        self.emp_lname.clear()
        self.radioButton_petite.setChecked(False)
        self.radioButton_classic.setChecked(False)
        self.radioButton_cash.setChecked(False)
        self.radioButton_gcash.setChecked(False)
        self.checkBox_1.setChecked(False)
        self.checkBox_2.setChecked(False)
        self.checkBox_3.setChecked(False)
        self.checkBox_4.setChecked(False)
        self.checkBox_5.setChecked(False)
        self.checkBox_6.setChecked(False)
        self.checkBox_7.setChecked(False)
        self.checkBox_1_qty.clear()
        self.checkBox_2_qty.clear()
        self.checkBox_3_qty.clear()
        self.checkBox_4_qty.clear()
        self.checkBox_7_qty.clear()

    def delete_bill(self):
        selected_row = self.bill_list.currentRow()
        if selected_row != -1:
            confirmation = QMessageBox.question(self, "Delete Bill", "Are you sure you want to delete this bill?", QMessageBox.Yes | QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                try:
                    conn = self.create_database_connection()
                    cur = conn.cursor()

                    # Get the bill id from the selected row
                    bill_num_item = self.bill_list.item(selected_row, 0)
                    if bill_num_item is not None:
                        bill_num = bill_num_item.text()

                        cur.execute("DELETE FROM BILL WHERE BILL_NUM = %s", (bill_num,))

                        # Commit the transaction
                        conn.commit()

                        self.bill_list.removeRow(selected_row)
                        QMessageBox.information(self, "Delete Bill", "Bill deleted successfully.")

                    else:
                        QMessageBox.warning(self, "Delete Bill", "Selected row does not contain bill information.")

                except psycopg2.Error as e:
                    QMessageBox.critical(self, "Database Error", "Error deleting bill from the database: " + str(e))
                finally:
                    if conn:
                        cur.close()
                        conn.close()

            else:
                QMessageBox.warning(self, "Delete Bill", "Deletion canceled.")
        else:
            QMessageBox.warning(self, "Delete Bill", "Select a row in the billing list to delete.")

    def download_bill(self):
        selected_row = self.bill_list.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Download Bill", "Select a row in the billing list to download.")
            return
        
        # Check if any row is selected
        if len(self.bill_list.selectedItems()) != self.bill_list.columnCount():
            QMessageBox.warning(self, "Download Bill", "Please select only one row to download.")
            return

        # Get column names
        column_names = [self.bill_list.horizontalHeaderItem(col).text() for col in range(self.bill_list.columnCount())]

        # Get bill data for the selected row
        bill_data = []
        for column in range(self.bill_list.columnCount()):
            item = self.bill_list.item(selected_row, column)
            bill_data.append(item.text())

        # Generate unique filename
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = "{}_{}.pdf".format(bill_data[0], current_datetime)
        default_path = os.path.expanduser("~/Downloads/{}".format(default_filename))

        pdf = SimpleDocTemplate(
            default_path,
            pagesize=letter,
            leftMargin=2.5 * inch,
            rightMargin=2.5 * inch,
            topMargin=1 * inch,
            bottomMargin=1 * inch
        )  # Create PDF document with 1-inch margins
        elements = []

        # Draw a border
        def draw_border(canvas, doc):
            canvas.saveState()
            canvas.setStrokeColor(colors.black)
            canvas.setLineWidth(1)
            canvas.rect(doc.leftMargin, doc.bottomMargin, doc.width, doc.height)
            canvas.restoreState()

        pdf.build(elements, onFirstPage=draw_border, onLaterPages=draw_border)

        logo_path = "D:/JVFILES/UclicK/venv/images/logo-receipt.jpg"
        elements.append(Spacer(1, 10))  # Add a spacer with a height of 20 units
        logo = Image(logo_path, width=200, height=75)
        elements.append(logo)

        # Add header
        elements.append(Spacer(1, 10))
        styles = getSampleStyleSheet()
        heading_style = ParagraphStyle(name='Heading1', fontSize=8, alignment=TA_CENTER)
        elements.append(Paragraph("<b>Uclick Self-Portrait Studio Lapu-Lapu</b>", heading_style))
        elements.append(Spacer(1, 10)) # Add a spacer
        elements.append(Paragraph("2F City Time Square Mactan, Lapu-Lapu City, Cebu, 6015", heading_style))
        elements.append(Spacer(1, 10)) # Add a spacer
        elements.append(Paragraph("by Sam Orlanes Photography", heading_style))
        elements.append(Spacer(1, 20)) # Add a spacer

        body_style = ParagraphStyle(name='Body', fontSize=8, alignment=TA_LEFT, leftIndent=10)
        body2_style = ParagraphStyle(name='Body', fontSize=12, alignment=TA_LEFT, leftIndent=10)
        elements.append(Paragraph("Employee: Owner", body_style))
        elements.append(Spacer(1, 10)) # Add a spacer
        elements.append(Paragraph("POS: Uclick Tab", body_style))
        elements.append(Spacer(1, 10)) # Add a spacer
        elements.append(Paragraph(f"<b>Bill #: {bill_data[0]}</b>", body2_style))
        elements.append(Spacer(1, 10)) # Add a spacer
        elements.append(Paragraph("...................................................................................................", body_style))
        elements.append(Spacer(1, 10)) # Add a spacer

        # Define client information
        client_info = [
            ["Client Name:", bill_data[7]],
            ["Number:", bill_data[8]],
            ["Email:", bill_data[9]]
        ]

        # Add vertical table for client information
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        table = Table(client_info, colWidths=[80, 120], style=style)
        elements.append(table)
        elements.append(Spacer(1, 10)) # Add a spacer 
        elements.append(Paragraph("...................................................................................................", body_style))
        elements.append(Spacer(1, 10)) # Add a spacer

        # Define package information
        package_info = [
            ["Session Date:", bill_data[1]],
            ["Package:", bill_data[2]],
            ["Additional:", bill_data[3]]
        ]

        # Add vertical table for package information
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        table = Table(package_info, colWidths=[80, 120], style=style)
        elements.append(table)
        elements.append(Spacer(1, 10)) # Add a spacer 
        elements.append(Paragraph("...................................................................................................", body_style))
        elements.append(Spacer(1, 10)) # Add a spacer

        # Calculate the change
        total_amount_due = float(bill_data[4])
        amount_paid = float(bill_data[5])
        change = amount_paid - total_amount_due

        # Define package information
        payment_info = [
            ["Total", f"P {bill_data[4]}"],
            ["Mode:", bill_data[6]],
            ["Amount Paid:", f"P {bill_data[5]}"],
            ["Change:", f"P {change:.2f}"]
        ]

        # Add vertical table for package information
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        table = Table(payment_info, colWidths=[80, 120], style=style)
        elements.append(table)
        elements.append(Spacer(1, 10)) # Add a spacer 
        elements.append(Paragraph("...................................................................................................", body_style))
        elements.append(Spacer(1, 10)) # Add a spacer

        elements.append(Paragraph(f"<b>Issued by: {bill_data[10]}</b>", body_style))
        elements.append(Spacer(1, 20)) # Add a spacer
        footer_style = ParagraphStyle(name='Heading1', fontSize=6, alignment=TA_CENTER)
        elements.append(Paragraph("Please note that all payments are non-refundable.", footer_style))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph("For any inquiries, please contact us at uclickstudio@gmail.com. Thank you!", footer_style))
        
        pdf.build(elements)
        QMessageBox.information(self, "Download Bill", "Bill downloaded successfully.")

    def send_bill_to_email(self):
        # Check if a row is selected
        selected_row = self.bill_list.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Send Email", "Please select a row in the billing list to send the email.")
            return

        # Get client's email from the selected row
        client_email = self.bill_list.item(selected_row, 9).text()  

        # Check if client's email is available
        if not client_email:
            QMessageBox.warning(self, "Send Email", "Client's email not found.")
            return

        # Retrieve billing information
        subject = "Your Billing Receipt"  # Subject of the email
        body = "Dear Customer,\n\nYour billing receipt is attached for your reference.\n\nRegards,\nUclicK Self-Portrait Studio"  # Body of the email

        # Construct the URL for composing the email in Gmail
        url = "https://mail.google.com/mail/?view=cm&to={}&su={}&body={}".format(
            quote(client_email), quote(subject), quote(body)
        )

        webbrowser.open(url)

    def show_logout_confirmation(self):
        confirmation = QMessageBox.question(self, "Logout", "Are you sure you want to logout?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            self.perform_logout()
        else:
            self.cancel_logout()
    
    def cancel_logout(self):
        QMessageBox.information(self, "Logout", "Logout canceled.")
        if self.current_index != -1 and 0 <= self.previous_button_index < len(self.sidebar_buttons):
            previous_button = self.sidebar_buttons[self.previous_button_index]
            previous_button.setChecked(True)

    def perform_logout(self):
        QMessageBox.information(self, "Logout", "Logged out successfully")
        self.logout_successful.emit()

    def create_database_connection(self):
        return psycopg2.connect(
            host='localhost',
            dbname='UclicK',
            user='postgres',
            password='password'
        )
    
class MainWidget(QMainWindow):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.stacked_widget = QStackedWidget()  # Initialize a stacked widget to manage multiple screens
        self.setCentralWidget(self.stacked_widget)  # Set the stacked widget as the central widget of the main window
        self.login_screen = LoginScreen()   # Create instances of the login screen and dashboard
        self.dashboard = Dashboard()
        self.stacked_widget.addWidget(self.login_screen)    # Add the login screen and dashboard to the stacked widget
        self.stacked_widget.addWidget(self.dashboard) 
        # Connect the login_successful signal from the login screen to show_login_successful_message slot
        self.login_screen.login_successful.connect(self.show_login_successful_message) 
        # Connect the logout_successful signal from the dashboard to show_login_screen slot
        self.dashboard.logout_successful.connect(self.show_login_screen)

    def show_login_successful_message(self):    # Slot to handle the successful login message
        QMessageBox.information(self, "Login", "Login Successful")  # Display an information message for successful login
        self.show_dashboard_screen()    # Switch to the dashboard screen
        self.login_screen.error.clear() # Clear any previous error message in the login screen

    def show_dashboard_screen(self):    # Switch to the dashboard screen
        self.stacked_widget.setCurrentWidget(self.dashboard)

    def show_login_screen(self):    # Switch to the login screen
        self.stacked_widget.setCurrentWidget(self.login_screen)
        self.login_screen.username.clear()
        self.login_screen.password.clear()

if __name__ == "__main__":  # Main block to execute the application
    app = QApplication(sys.argv)        # Create a QApplication instance
    main_widget = MainWidget()          # Create the main widget instance
    main_widget.setFixedSize(900, 650)  # Set the fixed size of the main widget
    main_widget.show()                  # Show the main widget
    sys.exit(app.exec_())               # Start the application event loop