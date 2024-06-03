import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLineEdit, QButtonGroup, QMessageBox, QTableWidgetItem, QFileDialog, QHeaderView
from PyQt5.uic import loadUi
import resources_rc
import psycopg2
from PyQt5.QtCore import QObject, pyqtSignal, QTime, QDate, QDateTime, Qt
from PyQt5.QtGui import QFont, QPixmap
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
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

    def toggle_password_visibility(self):
        if self.password.echoMode() == QLineEdit.Password:
            self.password.setEchoMode(QLineEdit.Normal)
        else:
            self.password.setEchoMode(QLineEdit.Password)

    def loginfunction(self):
        user = self.username.text()
        password = self.password.text()

        if len(user) == 0 or len(password) == 0:
            self.error.setText("Please fill in all fields.")
            return

        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(
                host='localhost',
                port='5432',
                dbname='UclicK',
                user='postgres',
                password='password',
                sslmode='prefer',
                connect_timeout=10
            )
            
            cur = conn.cursor() # Create a cursor object
            
            # Execute a query to retrieve user information
            cur.execute("SELECT EMP_USERNAME, EMP_PASSWORD FROM EMPLOYEE WHERE EMP_USERNAME = %s AND EMP_PASSWORD = %s", (user, password))
            
            result = cur.fetchone() # Fetch the result

            if result and result[1] == password:
                self.login_successful.emit()
                self.username.clear()
                self.password.clear()

            else:
                QMessageBox.warning(self, "Login", "Invalid username or password")
            
            # Close the cursor and connection
            cur.close()
            conn.close()

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error connecting to the database: " + str(e))

    def forgot_password(self):
        QMessageBox.information(self, "Forgot Password", "Oops! It seems like you've forgotten your password. Please contact the administrator to reset your password.")

class GuestBooking(QMainWindow):
    def __init__(self):
        super(GuestBooking, self).__init__()
        loadUi(r"D:\JVFILES\UclicK\venv\guestBooking.ui", self)
        self.stackedWidget.setCurrentIndex(0)
        self.guestmode_backButton.clicked.connect(self.go_to_login_screen)
        self.book_nowButton.clicked.connect(self.go_to_select_package)
        self.selectpackage_backButton.clicked.connect(self.go_to_guest_mode)
        self.selectpackage_nextButton.clicked.connect(self.go_to_select_extra)
        self.selectextra_backButton.clicked.connect(self.go_to_select_package)
        self.selectextra_nextButton.clicked.connect(self.go_to_req_datetime)
        self.skipButton.clicked.connect(self.skip_and_go_to_req_datetime)
        self.reqdatetime_backButton.clicked.connect(self.go_to_select_extra)
        self.reqdatetime_nextButton.clicked.connect(self.go_to_reviewreq)
        self.reviewbackButton.clicked.connect(self.skip_and_go_to_req_datetime)
        self.requestButton.clicked.connect(self.request_sent)
        self.okButton.clicked.connect(self.go_to_guest_mode)
        self.cancel1.clicked.connect(self.go_to_guest_mode)
        self.cancel2.clicked.connect(self.go_to_guest_mode)
        self.cancel3.clicked.connect(self.go_to_guest_mode)
        self.cancel4.clicked.connect(self.go_to_guest_mode)

    def go_to_login_screen(self):
        main_widget = self.parentWidget().parentWidget()  # Access MainWidget
        main_widget.show_login_screen()  # Show login screen
        main_widget.login_screen.username.clear()
        main_widget.login_screen.password.clear()
        main_widget.login_screen.error.clear()

    def go_to_guest_mode(self):
        self.stackedWidget.setCurrentIndex(0)

    def go_to_select_package(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_to_select_extra(self):
        if not self.checkBox_selectPetite.isChecked() and not self.checkBox_selectClassic.isChecked():
            QMessageBox.warning(self, "Select Package", "Please select a package.")
            return
        self.stackedWidget.setCurrentIndex(2)

    def go_to_req_datetime(self):
        if not any([self.checkBox_extraPerson.isChecked(), self.checkBox_extraKid.isChecked(), self.checkBox_extraPet.isChecked(), self.checkBox_extraPhotoPrint.isChecked(), self.checkBox_allSoftCopies.isChecked(), self.checkBox_advancePhotoEdit.isChecked()]):
            QMessageBox.warning(self, "Select Extra Services", "Please select any additional services or click Skip to proceed.")
            return
        self.stackedWidget.setCurrentIndex(3)
        if self.checkBox_selectPetite.isChecked():
            selected_package = "Petite"
            total_time = "Total time: 15 minutes"
        elif self.checkBox_selectClassic.isChecked():
            selected_package = "Classic"
            total_time = "Total time: 30 minutes"
        self.selectedpackage_label.setText(selected_package)
        self.totaltime_label.setText(total_time)

    def skip_and_go_to_req_datetime(self):
        self.stackedWidget.setCurrentIndex(3)
        if self.checkBox_selectPetite.isChecked():
            selected_package = "Petite"
            total_time = "Total time: 15 minutes"
        elif self.checkBox_selectClassic.isChecked():
            selected_package = "Classic"
            total_time = "Total time: 30 minutes"
        self.selectedpackage_label.setText(selected_package)
        self.totaltime_label.setText(total_time)

    def go_to_reviewreq(self):
        if not any([self.checkBox_11am.isChecked(), self.checkBox_1130am.isChecked(), self.checkBox_12pm.isChecked(), self.checkBox_1230pm.isChecked(), self.checkBox_1pm.isChecked(), self.checkBox_130pm.isChecked(), self.checkBox_2pm.isChecked(), self.checkBox_230pm.isChecked(), self.checkBox_3pm.isChecked(), self.checkBox_330pm.isChecked(), self.checkBox_4pm.isChecked(), self.checkBox_430pm.isChecked(), self.checkBox_5pm.isChecked(), self.checkBox_530pm.isChecked(), self.checkBox_6pm.isChecked(), self.checkBox_630pm.isChecked()]):
            QMessageBox.warning(self, "Request Time", "Please request time for your appointment.")
            return
        self.stackedWidget.setCurrentIndex(4)

        # Calculate the start time based on the checked checkboxes
        start_time = None
        for checkbox, time in zip(
            [self.checkBox_11am, self.checkBox_1130am, self.checkBox_12pm, self.checkBox_1230pm,
            self.checkBox_1pm, self.checkBox_130pm, self.checkBox_2pm, self.checkBox_230pm,
            self.checkBox_3pm, self.checkBox_330pm, self.checkBox_4pm, self.checkBox_430pm,
            self.checkBox_5pm, self.checkBox_530pm, self.checkBox_6pm, self.checkBox_630pm],
            [QTime(11, 0), QTime(11, 30), QTime(12, 0), QTime(12, 30),
            QTime(13, 0), QTime(13, 30), QTime(14, 0), QTime(14, 30),
            QTime(15, 0), QTime(15, 30), QTime(16, 0), QTime(16, 30),
            QTime(17, 0), QTime(17, 30), QTime(18, 0), QTime(18, 30)]
        ):
            if checkbox.isChecked():
                start_time = time
                break

        if start_time is None:
            QMessageBox.warning(self, "Select Time", "Please select a time.")
            return

        # Calculate end time based on the selected package
        if self.checkBox_selectPetite.isChecked():
            end_time = start_time.addSecs(15 * 60)  # Add 15 minutes
        elif self.checkBox_selectClassic.isChecked():
            end_time = start_time.addSecs(30 * 60)  # Add 30 minutes

        # Format the time strings
        start_time_str = start_time.toString("h:mm AP")
        end_time_str = end_time.toString("h:mm AP")
        self.book_time.setText(start_time_str + " - " + end_time_str) # Update the QLabel text with the selected time range

        selected_date = self.calendarpickdate.selectedDate().toString("ddd, MMMM dd, yyyy")
        self.book_date.setText(selected_date)

        if self.checkBox_selectPetite.isChecked():
            selected_package = "Petite"
            packg_desc = "PHP 600\n1-2 pax\n1 backdrop\n15 mins self-shoot session\n10 mins photo selection\n2 photo prints (1 full / 1 grid)\n5 digital copies (color enhanced)\nThere will be a charge in excess of 2 pax for \nthis package."
        elif self.checkBox_selectClassic.isChecked():
            selected_package = "Classic"
            packg_desc = "PHP 1,200\n1-4 pax\nUnlimited backdrop\n30 mins self-shoot session\n20 mins photo selection\n4 photo prints (2 full / 2 grid)\n10 digital copies (color enhanced)\nThere will be a charge in excess of 4 pax for \nthis package."
        self.package_review.setText(selected_package)
        self.packgdesc_label.setText(packg_desc)

    def validate_inputs(self):
        # Validate QLineEdit fields
        fields = [
            self.book_cli_fname, self.book_cli_lname,
            self.book_cli_contact, self.book_cli_email
        ]
        for field in fields:
            if field.text().strip() == "":
                QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
                return False

        # Validate email format
        email = self.book_cli_email.text().strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Email Error", "Please enter a valid email address.")
            return False
        
        return True
    
    def request_sent(self):
        # Validate inputs before inserting into the database
        if not self.validate_inputs():
            return
        
        # Confirmation dialog
        confirm_dialog = QMessageBox()
        confirm_dialog.setIcon(QMessageBox.Question)
        confirm_dialog.setWindowTitle("Confirmation")
        confirm_dialog.setText("Are you sure you want to submit the request?")
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        result = confirm_dialog.exec_()
        
        # Proceed with insertion into the database if the user clicked Yes
        if result == QMessageBox.Yes:
            try:
                conn = psycopg2.connect(
                    host='localhost',
                    port='5432',
                    dbname='UclicK',
                    user='postgres',
                    password='password',
                    sslmode='prefer',
                    connect_timeout=10
                )

                cur = conn.cursor()

                # Generate book_num based on current datetime
                current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
                book_num = current_datetime

                # Insert values into the BOOKING table
                cur.execute("""
                    INSERT INTO booking (BOOK_NUM, BOOK_PACKAGE, BOOK_DATE, BOOK_TIME,
                                        BOOK_CLI_FNAME, BOOK_CLI_LNAME,
                                        BOOK_CLI_CONTACT, BOOK_CLI_EMAIL, BOOK_NOTES)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    book_num,
                    self.package_review.text(),  # Use .text() to get the text of QLabel
                    self.calendarpickdate.selectedDate().toString("yyyy-MM-dd"),
                    self.book_time.text(),  # Assuming book_time QLabel is updated properly
                    self.book_cli_fname.text().strip(),
                    self.book_cli_lname.text().strip(),
                    self.book_cli_contact.text().strip(),
                    self.book_cli_email.text().strip(),
                    self.guestbooking_notes.toPlainText().strip()
                ))

                conn.commit()
                cur.close()
                conn.close()

                # Success message
                QMessageBox.information(self, "Request Sent", "Your request has been sent. You will receive a message as response. If you wish to cancel, please reply to our message.")
                self.stackedWidget.setCurrentIndex(5)  # Proceed to the next page

            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error connecting to the database: " + str(e))

class Dashboard(QMainWindow):
    logout_successful = pyqtSignal()
    
    def __init__(self):
        super(Dashboard, self).__init__()
        loadUi(r"D:\JVFILES\UclicK\venv\dashboard.ui", self)
        self.sidebar_buttons = [self.dashboard_button, self.appointments_button, self.clients_button, self.billing_button]
        self.current_index = 0
        self.stackedWidget.setCurrentIndex(0) # Initially show dashboard
        self.display_booking_status_chart()  # Display booking status chart
        self.display_total_appointments()
        self.display_total_clients()
        self.display_total_bills()
        self.dashboard_button.clicked.connect(self.show_dashboard)
        self.appButton.clicked.connect(self.show_appointments)
        self.appointments_button.clicked.connect(self.show_all_bookings)
        self.appButton.clicked.connect(self.show_all_bookings)
        self.appointments_button.clicked.connect(self.show_all_appointments)
        self.appButton.clicked.connect(self.show_all_appointments)
        self.appointments_button.clicked.connect(self.update_pending_labels)
        self.appButton.clicked.connect(self.update_pending_labels)
        self.book_petite_pending.clicked.connect(self.show_petite_pending_bookings)
        self.bookpetite_pending_nextButton.clicked.connect(self.next_petite_pending_booking)
        self.bookpetite_pending_backButton.clicked.connect(self.prev_petite_pending_booking)
        self.bookpetite_pending_closeButton.clicked.connect(self.show_appointments)
        self.bookpetite_pending_cancelButton.clicked.connect(self.cancel_petite_pending_booking) 
        self.bookpetite_pending_confirmButton.clicked.connect(self.confirm_petite_pending_booking)
        self.book_classic_pending.clicked.connect(self.show_classic_pending_bookings)
        self.bookclassic_pending_nextButton.clicked.connect(self.next_classic_pending_booking)
        self.bookclassic_pending_backButton.clicked.connect(self.prev_classic_pending_booking)
        self.bookclassic_pending_closeButton.clicked.connect(self.show_appointments)
        self.bookclassic_pending_cancelButton.clicked.connect(self.cancel_classic_pending_booking) 
        self.bookclassic_pending_confirmButton.clicked.connect(self.confirm_classic_pending_booking)
        self.search_booking_button.clicked.connect(self.search_bookings)
        self.delete_booking_button.clicked.connect(self.delete_booking)
        self.send_booking_button.clicked.connect(self.send_email_for_booking)
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
        self.current_petite_booking_index = 0
        self.petite_bookings = []
        self.current_classic_booking_index = 0
        self.classic_bookings = []
        self.current_pending_petite_appointment_index = 0
        self.petite_pending_appointments = []
        self.current_pending_classic_appointment_index = 0
        self.classic_pending_appointments = []
        self.current_complete_petite_appointment_index = 0
        self.petite_complete_appointments = []
        self.current_complete_classic_appointment_index = 0
        self.classic_complete_appointments = []
        self.clientButton.clicked.connect(self.show_clients)
        self.current_client_info_index = []
        self.client_info = []
        self.current_client_edit_index = []
        self.client_edit = []
        self.client_histButton.clicked.connect(self.client_appointment_history)
        self.bookhist_closeButton.clicked.connect(self.show_clients)
        self.search_apphist_button.clicked.connect(self.search_client_app_hist)
        self.client_editButton.clicked.connect(self.edit_client_info)
        self.client_editinfo_cancelButton.clicked.connect(self.show_clients)
        self.client_editinfo_saveButton.clicked.connect(self.confirm_save_changes)
        self.client_viewButton.clicked.connect(self.view_client_info)
        self.clientinfo_backButton.clicked.connect(self.prev_client_info)
        self.clientinfo_nextButton.clicked.connect(self.next_client_info)
        self.clientinfo_closeButton.clicked.connect(self.show_clients)
        self.billButton.clicked.connect(self.show_billing)
        self.appointments_button.clicked.connect(self.show_appointments)
        self.clients_button.clicked.connect(self.show_clients)
        self.search_client_button.clicked.connect(self.search_clients)
        self.billing_button.clicked.connect(self.show_billing)
        self.search_bill_button.clicked.connect(self.search_bills)
        self.generate_bill_button.clicked.connect(self.generate_bill)
        self.clear_button.clicked.connect(self.clear_fields)
        self.delete_button.clicked.connect(self.delete_bill)
        self.download_button.clicked.connect(self.download_bill)
        self.send_button.clicked.connect(self.send_bill_to_email)
        self.logout_button.clicked.connect(self.show_logout_confirmation)
         
    def show_dashboard(self):
        self.stackedWidget.setCurrentIndex(0)
        self.current_index = 0
        self.dashboard_button.setChecked(True)
        self.previous_button_index = 0
        
    def display_booking_status_chart(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*), BOOK_STATUS FROM BOOKING GROUP BY BOOK_STATUS")
            status_counts = cur.fetchall()
            
            counts = [0, 0, 0]
            status_names = ['Cancelled', 'Pending', 'Confirmed']
            
            for status_count in status_counts:
                status_name = status_count[1]
                count = status_count[0]
                if status_name in status_names:
                    index = status_names.index(status_name)
                    counts[index] = count

            # Define colors
            colors = ['#0A7CEB', '#32A4FF', '#4682B4']  # Different shades of blue in order: (Cancelled, Pending, Confirmed)
            
            # Plot pie chart
            plt.clf()
            plt.figure(figsize=(6.01, 3.51))
            plt.pie(counts, colors=colors, autopct='%d%%', startangle=140, textprops={'color': 'white', 'fontsize': 12})
            plt.axis('equal')
            plt.savefig('booking_status_pie_chart.png', transparent=True) # Save the chart as an image with transparent background

            # Display the chart in a QLabel
            pixmap = QPixmap('booking_status_pie_chart.png')
            self.booking_status_chart.setPixmap(pixmap)
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error connecting to the database: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def display_total_appointments(self):
        conn = None
        try:
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

    def display_total_clients(self):
        conn = None
        try:
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

    def display_total_bills(self):
        conn = None
        try:
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
            
    def show_appointments(self):
        self.stackedWidget.setCurrentIndex(1)
        self.current_index = 1
        self.appointments_button.setChecked(True) 
        self.previous_button_index = 1

    def show_all_bookings(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor() 
            cur.execute("SELECT * FROM BOOKING")
            result = cur.fetchall() 
            
            self.bookTable.setRowCount(len(result))
            self.bookTable.setColumnCount(9)  # Adjust the column count
            column_names = ['Booking Number', 'Package', 'Date', 'Time', 'Address', 'Client', 'Phone Number', 'Client Email', 'Status']
            self.bookTable.setHorizontalHeaderLabels(column_names)
            font = QFont()
            font.setBold(True)
            font.setPointSize(12) 
            self.bookTable.horizontalHeader().setFont(font)
            for i, row in enumerate(result):
                for j, value in enumerate(row):
                    if j == 5:  # If it's the Client column
                        client_info = f"{row[5]} {row[6]}"  # Concatenate Client and Client Name
                        item = QTableWidgetItem(client_info)
                    elif j == 6:  # If it's the Phone Number column
                        continue  # Skip this column, as it's concatenated with the Client column
                    else:
                        item = QTableWidgetItem(str(value))
                    # Adjust the column index
                    if j > 6:
                        self.bookTable.setItem(i, j-1, item)  # Skip the Phone Number column
                    else:
                        self.bookTable.setItem(i, j, item)

            # Resize columns to fit contents
            self.bookTable.resizeColumnsToContents()
            self.bookTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error loading booking data: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def show_all_appointments(self):
        conn = None
        try:
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

    def update_pending_labels(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor() 

            # Query for counting bookings and appointments to review for each package
            cur.execute("SELECT COUNT(*) FROM BOOKING WHERE book_status = 'Pending' AND book_package = 'Petite'")
            count_petite = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM BOOKING WHERE book_status = 'Pending' AND book_package = 'Classic'")
            count_classic = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE app_status IN ('Pending', 'Rescheduled') AND app_package = 'Petite'")
            count_petite_app_pending = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE app_status = 'Complete' AND app_package = 'Petite'")
            count_petite_app_completed = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE app_status IN ('Pending', 'Rescheduled') AND app_package = 'Classic'")
            count_classic_app_pending = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE app_status = 'Complete' AND app_package = 'Classic'")
            count_classic_app_completed = cur.fetchone()[0]

            # Update labels
            self.book_petite_pending_label.setText(f"{count_petite} bookings to review")
            self.book_classic_pending_label.setText(f"{count_classic} bookings to review")
            self.app_petite_pending_label.setText(f"{count_petite_app_pending} appointments to review")
            self.app_petite_completed_label.setText(f"{count_petite_app_completed} appointments to review")
            self.app_classic_pending_label.setText(f"{count_classic_app_pending} appointments to review")
            self.app_classic_completed_label.setText(f"{count_classic_app_completed} appointments to review")

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error updating pending labels: " + str(e))
        finally:
            if conn:
                cur.close()
                conn.close()

    def show_petite_pending_bookings(self):
        self.stackedWidget.setCurrentIndex(2)
        self.petite_bookings = self.fetch_petite_pending_bookings()
        self.current_petite_booking_index = 0
        self.display_petite_pending_booking(self.current_petite_booking_index)

    def fetch_petite_pending_bookings(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor() 
            cur.execute("SELECT * FROM BOOKING WHERE book_status = 'Pending' AND book_package = 'Petite'")
            return cur.fetchall()
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error loading petite pending bookings: " + str(e))
            return []
        finally:
            if conn:
                cur.close()
                conn.close()

    def display_petite_pending_booking(self, index):
        if index < len(self.petite_bookings):
            booking = self.petite_bookings[index]
            self.bookpetite_pending_client_label.setText(f"{booking[5]} {booking[6]}")
            self.bookpetite_pending_datetime_label.setText(f"{booking[2]}  {booking[3]}")
            self.bookpetite_pending_notes.setText(f"{booking[10]}")           
        else:
            QMessageBox.warning(self, "Warning", "No more pending bookings to display.")
        
    def next_petite_pending_booking(self):
        self.current_petite_booking_index += 1
        self.display_petite_pending_booking(self.current_petite_booking_index)
        
    def prev_petite_pending_booking(self):
        if self.current_petite_booking_index > 0:
            self.current_petite_booking_index -= 1
            self.display_petite_pending_booking(self.current_petite_booking_index)
        else:
            QMessageBox.warning(self, "Warning", "This is the first pending booking.")

    def cancel_petite_pending_booking(self):
        confirmation = QMessageBox.question(self, "Cancel Booking", "Are you sure you want to cancel this booking?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            booking = self.petite_bookings[self.current_petite_booking_index]  # Get the current pending booking
            
            # Update the status to 'Cancelled' in the database
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor() 
                cur.execute("UPDATE BOOKING SET book_status = 'Cancelled' WHERE book_num = %s", (booking[0],))
                conn.commit()
                QMessageBox.information(self, "Cancellation", "Booking Cancelled Successfully")
                
                self.petite_bookings.pop(self.current_petite_booking_index)  # Remove the cancelled booking from the list
                
                # Update the pie chart, booking table, and pending label
                self.display_booking_status_chart()
                self.show_all_bookings()
                self.update_pending_labels()
                
                # Display next pending booking if available
                if self.current_petite_booking_index < len(self.petite_bookings):
                    self.display_petite_pending_booking(self.current_petite_booking_index)
                elif self.current_petite_booking_index > 0:
                    self.current_petite_booking_index -= 1
                    self.display_petite_pending_booking(self.current_petite_booking_index)
                else:
                    self.bookpetite_pending_client_label.clear()
                    self.bookpetite_pending_datetime_label.clear()
                    self.bookpetite_pending_notes.clear()
                    QMessageBox.warning(self, "Warning", "No more pending bookings to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error cancelling booking: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def confirm_petite_pending_booking(self):
        confirmation = QMessageBox.question(self, "Confirm Booking", "Are you sure you want to confirm this booking?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            booking = self.petite_bookings[self.current_petite_booking_index]  # Get the current pending booking

            # Update the status to 'Confirmed' in the database
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor() 
                cur.execute("UPDATE BOOKING SET book_status = 'Confirmed' WHERE book_num = %s", (booking[0],))
                conn.commit()
                QMessageBox.information(self, "Confirmation", "Booking Confirmed Successfully")
                
                # Generate client code
                client_code = self.generate_client_code(booking[5], booking[6])
                
                # Insert or get existing client
                client_code = self.insert_or_get_client(conn, cur, booking, client_code)
                
                # Insert into APPOINTMENT table
                appointment_num = self.generate_appointment_num()
                self.insert_into_appointment(conn, cur, booking, client_code, appointment_num)
                
                self.petite_bookings.pop(self.current_petite_booking_index)  # Remove the confirmed booking from the list
                
                # Update the pie chart, labels, and tables
                self.display_booking_status_chart()
                self.display_total_appointments()
                self.display_total_clients()
                self.show_all_bookings()
                self.show_all_appointments()
                self.update_pending_labels()
                
                # Display next pending booking if available
                if self.current_petite_booking_index < len(self.petite_bookings):
                    self.display_petite_pending_booking(self.current_petite_booking_index)
                elif self.current_petite_booking_index > 0:
                    self.current_petite_booking_index -= 1
                    self.display_petite_pending_booking(self.current_petite_booking_index)
                else:
                    self.bookpetite_pending_client_label.clear()
                    self.bookpetite_pending_datetime_label.clear()
                    self.bookpetite_pending_notes.clear()
                    QMessageBox.warning(self, "Warning", "No more pending bookings to display.")
                
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error confirming booking: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def show_classic_pending_bookings(self):
        self.stackedWidget.setCurrentIndex(3)
        self.classic_bookings = self.fetch_classic_pending_bookings()
        self.current_classic_booking_index = 0
        self.display_classic_pending_booking(self.current_classic_booking_index)

    def fetch_classic_pending_bookings(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor() 
            cur.execute("SELECT * FROM BOOKING WHERE book_status = 'Pending' AND book_package = 'Classic'")
            return cur.fetchall()
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error loading petite pending bookings: " + str(e))
            return []
        finally:
            if conn:
                cur.close()
                conn.close()

    def display_classic_pending_booking(self, index):
        if index < len(self.classic_bookings):
            booking = self.classic_bookings[index]
            self.bookclassic_pending_client_label.setText(f"{booking[5]} {booking[6]}")
            self.bookclassic_pending_datetime_label.setText(f"{booking[2]}  {booking[3]}")
            self.bookclassic_pending_notes.setText(f"{booking[10]}")           
        else:
            QMessageBox.warning(self, "Warning", "No more pending bookings to display.")

    def next_classic_pending_booking(self):
        self.current_classic_booking_index += 1
        self.display_classic_pending_booking(self.current_classic_booking_index)

    def prev_classic_pending_booking(self):
        if self.current_classic_booking_index > 0:
            self.current_classic_booking_index -= 1
            self.display_classic_pending_booking(self.current_classic_booking_index)
        else:
            QMessageBox.warning(self, "Warning", "This is the first pending booking.")

    def cancel_classic_pending_booking(self):
        confirmation = QMessageBox.question(self, "Cancel Booking", "Are you sure you want to cancel this booking?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            booking = self.classic_bookings[self.current_classic_booking_index]  # Get the current pending booking
            
            # Update the status to 'Cancelled' in the database
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor() 
                cur.execute("UPDATE BOOKING SET book_status = 'Cancelled' WHERE book_num = %s", (booking[0],))
                conn.commit()
                QMessageBox.information(self, "Cancellation", "Booking Cancelled Successfully")
                
                self.classic_bookings.pop(self.current_classic_booking_index)  # Remove the cancelled booking from the list
                
                # Update the pie chart, booking table, and pending label
                self.display_booking_status_chart()
                self.show_all_bookings()
                self.update_pending_labels()
                
                # Display next pending booking if available
                if self.current_classic_booking_index < len(self.classic_bookings):
                    self.display_classic_pending_booking(self.current_classic_booking_index)
                elif self.current_classic_booking_index > 0:
                    self.current_classic_booking_index -= 1
                    self.display_classic_pending_booking(self.current_classic_booking_index)
                else:
                    self.bookclassic_pending_client_label.clear()
                    self.bookclassic_pending_datetime_label.clear()
                    self.bookclassic_pending_notes.clear()
                    QMessageBox.warning(self, "Warning", "No more pending bookings to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error cancelling booking: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def confirm_classic_pending_booking(self):
        confirmation = QMessageBox.question(self, "Confirm Booking", "Are you sure you want to confirm this booking?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            booking = self.classic_bookings[self.current_classic_booking_index]  # Get the current pending booking

            # Update the status to 'Confirmed' in the database
            conn = None
            try:
                conn = self.create_database_connection()
                cur = conn.cursor() 
                cur.execute("UPDATE BOOKING SET book_status = 'Confirmed' WHERE book_num = %s", (booking[0],))
                conn.commit()
                QMessageBox.information(self, "Confirmation", "Booking Confirmed Successfully")
                
                # Generate client code
                client_code = self.generate_client_code(booking[5], booking[6])
                
                # Insert or get existing client
                client_code = self.insert_or_get_client(conn, cur, booking, client_code)
                
                # Insert into APPOINTMENT table
                appointment_num = self.generate_appointment_num()
                self.insert_into_appointment(conn, cur, booking, client_code, appointment_num)
                
                self.classic_bookings.pop(self.current_classic_booking_index)  # Remove the confirmed booking from the list
                
                # Update the pie chart, labels, and tables
                self.display_booking_status_chart()
                self.display_total_appointments()
                self.display_total_clients()
                self.show_all_bookings()
                self.show_all_appointments()
                self.update_pending_labels()
                
                # Display next pending booking if available
                if self.current_classic_booking_index < len(self.classic_bookings):
                    self.display_classic_pending_booking(self.current_classic_booking_index)
                elif self.current_classic_booking_index > 0:
                    self.current_classic_booking_index -= 1
                    self.display_classic_pending_booking(self.current_classic_booking_index)
                else:
                    self.bookclassic_pending_client_label.clear()
                    self.bookclassic_pending_datetime_label.clear()
                    self.bookclassic_pending_notes.clear()
                    QMessageBox.warning(self, "Warning", "No more pending bookings to display.")
                
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error confirming booking: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def generate_client_code(self, fname, lname):
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{fname[0]}{current_datetime}{lname[0]}"
    
    def insert_or_get_client(self, conn, cur, booking, client_code):
        try:
            # Check if the client already exists
            cur.execute("SELECT client_code FROM CLIENT WHERE client_fname = %s AND client_lname = %s AND client_contact_number = %s AND client_email = %s",
                        (booking[5], booking[6], booking[7], booking[8]))
            existing_client = cur.fetchone()

            if not existing_client:
                # Insert into the client table
                cur.execute("INSERT INTO CLIENT (client_code, client_fname, client_lname, client_contact_number, client_email) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING RETURNING client_code",
                            (client_code, booking[5], booking[6], booking[7], booking[8]))
                conn.commit()
                return client_code
            else:
                return existing_client[0]  # Use existing client_code
        except psycopg2.Error as e:
            conn.rollback()
            raise e
    
    def generate_appointment_num(self):
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def insert_into_appointment(self, conn, cur, booking, client_code, appointment_num):
        try:
            cur.execute("""
                INSERT INTO APPOINTMENT (APP_NUM, BOOK_NUM, CLIENT_CODE, APP_DATE, APP_TIME, APP_ADDRESS, APP_STATUS, APP_NOTES, APP_PACKAGE) 
                SELECT %s, %s, %s, BOOK_DATE, BOOK_TIME, BOOK_ADDRESS, 'Pending', BOOK_NOTES, BOOK_PACKAGE
                FROM BOOKING 
                WHERE BOOK_NUM = %s
            """, (appointment_num, booking[0], client_code, booking[0]))
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise e

    def show_petite_pending_appointments(self):
        self.stackedWidget.setCurrentIndex(4)
        self.petite_pending_appointments = self.fetch_petite_pending_appointments()
        self.current_pending_petite_appointment_index = 0
        self.display_petite_pending_appointment(self.current_pending_petite_appointment_index)

    def fetch_petite_pending_appointments(self):
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

    def display_petite_pending_appointment(self, index):
        if index < len(self.petite_pending_appointments):
            appointment = self.petite_pending_appointments[index]
            client_code = appointment[2]  # Assuming appointment[2] is the client_code
            client_fname, client_lname = self.fetch_client_details(client_code)

            if client_fname and client_lname:
                self.apppetite_pending_client_label.setText(f"{client_fname} {client_lname}")
            else:
                self.apppetite_pending_client_label.setText("Unknown Client")
                
            self.apppetite_pending_datetime_label.setText(f"{appointment[3]}  {appointment[4]}")
            self.apppetite_pending_notes.setText(f"{appointment[7]}")           
        else:
            QMessageBox.warning(self, "Warning", "No more pending appointments to display.")

    def fetch_client_details(self, client_code):
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

    def next_petite_pending_appointment(self):
        self.current_pending_petite_appointment_index += 1
        self.display_petite_pending_appointment(self.current_pending_petite_appointment_index)

    def prev_petite_pending_appointment(self):
        if self.current_pending_petite_appointment_index > 0:
            self.current_pending_petite_appointment_index -= 1
            self.display_petite_pending_appointment(self.current_pending_petite_appointment_index)
        else:
            QMessageBox.warning(self, "Warning", "This is the first pending appointment.")

    def cancel_petite_pending_appointment(self):
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
                    self.apppetite_pending_notes.clear()
                    QMessageBox.warning(self, "Warning", "No more pending appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error cancelling appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def noshow_petite_pending_appointment(self):
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
                    self.apppetite_pending_notes.clear()
                    QMessageBox.warning(self, "Warning", "No more pending appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error cancelling appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def resched_petite_pending_appointment(self):
        self.stackedWidget.setCurrentIndex(5)

        # Retrieve current pending appointment
        if self.current_pending_petite_appointment_index < len(self.petite_pending_appointments):
            appointment = self.petite_pending_appointments[self.current_pending_petite_appointment_index]
            client_code = appointment[2]
            client_fname, client_lname = self.fetch_client_details(client_code)

            if client_fname and client_lname:
                self.apppetite_resched_client_label.setText(f"{client_fname} {client_lname}")
            else:
                self.apppetite_resched_client_label.setText("Unknown Client")
            self.apppetite_resched_origdatetime.setText(f"{appointment[3]}  {appointment[4]}")

            current_datetime = QDateTime.currentDateTime()
            self.apppetite_resched_datetime.setDateTime(current_datetime)
                
        else:
            QMessageBox.warning(self, "Warning", "No pending appointment to reschedule.")

    def petite_reschedule_save_button_clicked(self):
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

    def complete_petite_pending_appointment(self):
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
                    self.apppetite_pending_notes.clear()
                    QMessageBox.warning(self, "Warning", "No more pending appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error cancelling appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def show_petite_complete_appointments(self):
        self.stackedWidget.setCurrentIndex(6)
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
            client_code = appointment[2]  # Assuming appointment[2] is the client_code
            client_fname, client_lname = self.fetch_client_details(client_code)

            if client_fname and client_lname:
                self.apppetite_complete_client_label.setText(f"{client_fname} {client_lname}")
            else:
                self.apppetite_complete_client_label.setText("Unknown Client")
                
            self.apppetite_complete_datetime_label.setText(f"{appointment[3]}  {appointment[4]}")
            self.apppetite_complete_notes.setText(f"{appointment[7]}")           
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
                    self.apppetite_complete_notes.clear()
                    QMessageBox.warning(self, "Warning", "No more complete appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error undoing appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def show_classic_pending_appointments(self):
        self.stackedWidget.setCurrentIndex(7)
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
            client_code = appointment[2]  # Assuming appointment[2] is the client_code
            client_fname, client_lname = self.fetch_client_details(client_code)

            if client_fname and client_lname:
                self.appclassic_pending_client_label.setText(f"{client_fname} {client_lname}")
            else:
                self.appclassic_pending_client_label.setText("Unknown Client")
                
            self.appclassic_pending_datetime_label.setText(f"{appointment[3]}  {appointment[4]}")
            self.appclassic_pending_notes.setText(f"{appointment[7]}")           
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
                    self.appclassic_pending_notes.clear()
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
                    self.appclassic_pending_notes.clear()
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
            client_code = appointment[2]
            client_fname, client_lname = self.fetch_client_details(client_code)

            if client_fname and client_lname:
                self.appclassic_resched_client_label.setText(f"{client_fname} {client_lname}")
            else:
                self.appclassic_resched_client_label.setText("Unknown Client")
            self.appclassic_resched_origdatetime.setText(f"{appointment[3]}  {appointment[4]}")

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
                    self.appclassic_pending_notes.clear()
                    QMessageBox.warning(self, "Warning", "No more pending appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error cancelling appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def show_classic_complete_appointments(self): 
        self.stackedWidget.setCurrentIndex(8)
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
            client_code = appointment[2]  # Assuming appointment[2] is the client_code
            client_fname, client_lname = self.fetch_client_details(client_code)

            if client_fname and client_lname:
                self.appclassic_complete_client_label.setText(f"{client_fname} {client_lname}")
            else:
                self.appclassic_complete_client_label.setText("Unknown Client")
                
            self.appclassic_complete_datetime_label.setText(f"{appointment[3]}  {appointment[4]}")
            self.appclassic_complete_notes.setText(f"{appointment[7]}")           
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
                    self.appclassic_complete_notes.clear()
                    QMessageBox.warning(self, "Warning", "No more complete appointments to display.")
            
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Database Error", "Error undoing appointment: " + str(e))
            finally:
                if conn:
                    cur.close()
                    conn.close()

    def search_bookings(self):
        search_booking = self.search_booking.text().strip().lower()
        if not search_booking:
            return

        for row in range(self.bookTable.rowCount()):
            row_text = " ".join([self.bookTable.item(row, col).text().lower() for col in range(self.bookTable.columnCount())])
            if search_booking in row_text:
                self.bookTable.setRowHidden(row, False)
            else:
                self.bookTable.setRowHidden(row, True)

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

    def delete_booking(self):
        selected_row = self.bookTable.currentRow()
        if selected_row != -1:
            confirmation = QMessageBox.question(self, "Delete Booking", "Are you sure you want to delete this booking?", QMessageBox.Yes | QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                try:
                    conn = self.create_database_connection()
                    cur = conn.cursor()

                    # Get the booking number from the selected row
                    book_num_item = self.bookTable.item(selected_row, 0)
                    if book_num_item is not None:
                        book_num = book_num_item.text()

                        cur.execute("DELETE FROM BOOKING WHERE BOOK_NUM = %s", (book_num,))

                        # Commit the transaction
                        conn.commit()

                        self.bookTable.removeRow(selected_row)
                        QMessageBox.information(self, "Delete Booking", "Booking deleted successfully.")
                        self.show_all_bookings()
                        self.update_pending_labels()
                        self.display_booking_status_chart()

                    else:
                        QMessageBox.warning(self, "Delete Booking", "Selected row does not contain booking information.")

                except psycopg2.Error as e:
                    QMessageBox.critical(self, "Database Error", "Error deleting booking from the database: " + str(e))
                finally:
                    if conn:
                        cur.close()
                        conn.close()

            else:
                QMessageBox.warning(self, "Delete Booking", "Deletion canceled.")
        else:
            QMessageBox.warning(self, "Delete Booking", "Select a row in the booking table to delete.")

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

    def send_email_for_booking(self):
        # Check if a row is selected
        selected_row = self.bookTable.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Send Email", "Please select a row in the booking table to send the email.")
            return

        # Get booking details from the selected row
        package = self.bookTable.item(selected_row, 1).text()  
        date = self.bookTable.item(selected_row, 2).text()  
        time = self.bookTable.item(selected_row, 3).text()  
        address = self.bookTable.item(selected_row, 4).text()  
        client_email = self.bookTable.item(selected_row, 7).text()  
        booking_status = self.bookTable.item(selected_row, 8).text() 

        # Check if client's email is available
        if not client_email:
            QMessageBox.warning(self, "Send Email", "Client's email not found.")
            return

        # Construct email message based on booking status
        if booking_status == "Confirmed":
            subject = "Booking Confirmation"
            body = f"""Dear Customer,

Your booking for {package} on {date} at {time} is confirmed.
Location: {address}

We look forward to seeing you. Please arrive on time.

Regards,
Uclick Self-Portrait Studio"""
        elif booking_status == "Cancelled":
            subject = "Booking Cancelled"
            body = f"""Dear Customer,

Your booking for {package} on {date} at {time} is cancelled.
Location: {address}
Reasons:


We apologize for any inconvenience this may have caused. Please feel free to book another appointment at your convenience.

Regards,
Uclick Self-Portrait Studio"""

        # Construct the URL for composing the email in Gmail
        url = "https://mail.google.com/mail/?view=cm&to={}&su={}&body={}".format(
            quote(client_email), quote(subject), quote(body)
        )

        webbrowser.open(url)

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
        self.stackedWidget.setCurrentIndex(10)
        self.current_index = 10
        self.clients_button.setChecked(True)
        self.previous_button_index = 2
        self.load_clients_data()

    def load_clients_data(self):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor() 
            cur.execute("SELECT client_fname, client_lname, client_email, client_contact_number, COUNT(*) AS num_bookings FROM CLIENT LEFT JOIN APPOINTMENT ON CLIENT.client_code = APPOINTMENT.client_code GROUP BY CLIENT.client_code ORDER BY client_fname ASC, client_lname ASC")
            clients = cur.fetchall()

            self.client_list.setRowCount(len(clients))
            self.client_list.setColumnCount(5) 
            column_names = ['First Name', 'Last Name', 'Email Address', 'Contact Number', 'No. of Appointments']
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
            
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error loading client data: " + str(e))
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

    def view_client_info(self):
        # Get selected row
        selected_row = self.client_list.currentRow()
        if selected_row != -1:  # If a row is selected
            self.stackedWidget.setCurrentIndex(12)
            self.current_client_info_index = selected_row
            self.display_client_info(selected_row)
        else:
            QMessageBox.warning(self, "Warning", "Please select a client to view.")

    def display_client_info(self, index):
        if index >= 0 and index < self.client_list.rowCount():
            client_fname = self.client_list.item(index, 0).text()
            client_lname = self.client_list.item(index, 1).text()
            client_email = self.client_list.item(index, 2).text()
            client_contact = self.client_list.item(index, 3).text()
                
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
            client_fname = self.client_list.item(selected_row, 0).text()
            client_lname = self.client_list.item(selected_row, 1).text()
            client_email = self.client_list.item(selected_row, 2).text()
            client_contact = self.client_list.item(selected_row, 3).text()

            # Set data into line edits
            self.client_editinfo_fname.setText(client_fname)
            self.client_editinfo_lname.setText(client_lname)
            self.client_editinfo_email.setText(client_email)
            self.client_editinfo_contact.setText(client_contact)

            # Switch to the edit page
            self.stackedWidget.setCurrentIndex(11)
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
            original_fname = self.client_list.item(selected_row, 0).text()
            original_lname = self.client_list.item(selected_row, 1).text()
            original_email = self.client_list.item(selected_row, 2).text()
            original_contact = self.client_list.item(selected_row, 3).text()

            # Get client code based on the original data
            client_code = self.get_client_code(original_fname, original_lname, original_email, original_contact)

            if client_code:
                # Retrieve data from line edits
                edited_fname = self.client_editinfo_fname.text()
                edited_lname = self.client_editinfo_lname.text()
                edited_email = self.client_editinfo_email.text()
                edited_contact = self.client_editinfo_contact.text()

                # Update the selected row in the client list table
                self.client_list.item(selected_row, 0).setText(edited_fname)
                self.client_list.item(selected_row, 1).setText(edited_lname)
                self.client_list.item(selected_row, 2).setText(edited_email)
                self.client_list.item(selected_row, 3).setText(edited_contact)

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

    def get_client_code(self, fname, lname, email, contact):
        conn = None
        try:
            conn = self.create_database_connection()
            cur = conn.cursor()

            cur.execute("SELECT client_code FROM CLIENT WHERE client_fname = %s AND client_lname = %s AND client_email = %s AND client_contact_number = %s", 
                        (fname, lname, email, contact))
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                return None
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Database Error", "Error fetching client code: " + str(e))
            return None
        finally:
            if conn:
                cur.close()
                conn.close()

    def client_appointment_history(self):
        selected_row = self.client_list.currentRow()
        if selected_row != -1:  # If a row is selected
            # Retrieve original data from the selected row in the client list table
            original_fname = self.client_list.item(selected_row, 0).text()
            original_lname = self.client_list.item(selected_row, 1).text()
            original_email = self.client_list.item(selected_row, 2).text()
            original_contact = self.client_list.item(selected_row, 3).text()

            self.client_apphist.setText(f"Client: {original_fname} {original_lname}")

            # Get client code based on the original data
            client_code = self.get_client_code(original_fname, original_lname, original_email, original_contact)

            if client_code:
                # Fetch booking history from database
                conn = None
                try:
                    conn = self.create_database_connection()
                    cur = conn.cursor()

                    # Select appointments and bills for the given client code
                    cur.execute("SELECT a.app_date, a.app_time, a.app_package, bill.bill_add_services, bill.bill_amount_due, bill.bill_mode, a.app_status "
                                "FROM appointment AS a "
                                "LEFT JOIN bill ON a.app_num = bill.app_num "
                                "WHERE a.client_code = %s", (client_code,))
                    booking_history = cur.fetchall()

                    # Populate the client_app_history_table 
                    self.client_app_history_table.setRowCount(len(booking_history))
                    self.client_app_history_table.setColumnCount(7)
                    column_names = ['Date', 'Time', 'Package', 'Additional Services', 'Amount Due', 'Payment Mode', 'Status']
                    self.client_app_history_table.setHorizontalHeaderLabels(column_names)
                    font = QFont()
                    font.setBold(True)
                    font.setPointSize(12) 
                    self.client_app_history_table.horizontalHeader().setFont(font)

                    for i, (date, time, package, additional_services, amount_due, payment_mode, status) in enumerate(booking_history):
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

                    self.stackedWidget.setCurrentIndex(13)  # Switch to the booking history page
                except psycopg2.Error as e:
                    QMessageBox.critical(self, "Database Error", "Error fetching booking history: " + str(e))
                finally:
                    if conn:
                        cur.close()
                        conn.close()
            else:
                QMessageBox.warning(self, "Warning", "Client code not found for the selected client.")
        else:
            QMessageBox.warning(self, "Warning", "Please select a client to view booking history.")

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

    def show_billing(self):
        self.stackedWidget.setCurrentIndex(14)
        self.current_index = 14
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
                    C.CLIENT_EMAIL, E.EMP_FNAME || ' ' || E.EMP_LNAME AS EMP_NAME 
                FROM BILL B 
                LEFT JOIN CLIENT C ON B.CLIENT_CODE = C.CLIENT_CODE
                LEFT JOIN EMPLOYEE E ON B.EMP_CODE = E.EMP_CODE
            """)
            result = cur.fetchall() 

            self.bill_list.setRowCount(len(result))
            self.bill_list.setColumnCount(10) 
            column_names = ['Bill Number', 'Session Date', 'Package', 'Additional', 'Amount Due', 'Amount Paid', 'Mode', 'Client Name', 'Client Email', 'Issued by']
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

        # Transpose data for vertical table
        data = [[col_name] + [value] for col_name, value in zip(column_names, bill_data)]

        # Generate unique filename
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = "{}_{}.pdf".format(bill_data[0], current_datetime)
        default_path = os.path.expanduser("~/Downloads/{}".format(default_filename))

        pdf = SimpleDocTemplate(default_path, pagesize=letter) # Create PDF document
        elements = []

        logo_path = "D:/JVFILES/UclicK/venv/images/logo-header.jpg"
        logo = Image(logo_path, width=550, height=75)
        elements.append(logo)

        # Add billing information
        elements.append(Spacer(1, 60))
        styles = getSampleStyleSheet()
        heading_style = ParagraphStyle(name='Heading1', fontSize=32, alignment=TA_CENTER)
        elements.append(Paragraph("<b>Billing Information</b>", heading_style))
        elements.append(Spacer(1, 60)) # Add a spacer

        # Add vertical table
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        table = Table(data, style=style)
        elements.append(table)
        elements.append(Spacer(1, 100))
        p_style = ParagraphStyle(name='Heading1', fontSize=12, alignment=TA_CENTER)
        disclaimer_style = ParagraphStyle(name='Heading1', fontSize=8, alignment=TA_CENTER)
        elements.append(Paragraph("Thank you for choosing our services. Please note that all payments are non-refundable.", p_style))
        elements.append(Spacer(1, 28))
        elements.append(Paragraph("For any inquiries, please contact us at uclickstudio@gmail.com. Thank you!", p_style))
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("This is an electronic invoice and does not require a physical signature.", disclaimer_style))
        pdf.build(elements)
        QMessageBox.information(self, "Download Bill", "Bill downloaded successfully.")

    def send_bill_to_email(self):
        # Check if a row is selected
        selected_row = self.bill_list.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Send Email", "Please select a row in the billing list to send the email.")
            return

        # Get client's email from the selected row
        client_email = self.bill_list.item(selected_row, 8).text()  

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
            port='5432',
            dbname='UclicK',
            user='postgres',
            password='password',
            sslmode='prefer',
            connect_timeout=10
        )
    
class MainWidget(QMainWindow):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.login_screen = LoginScreen()
        self.guest_booking = GuestBooking()
        self.dashboard = Dashboard()
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.guest_booking)
        self.stacked_widget.addWidget(self.dashboard) 
        self.login_screen.guest.clicked.connect(self.show_guest_booking_screen)
        self.login_screen.login_successful.connect(self.show_login_successful_message)
        self.dashboard.logout_successful.connect(self.show_login_screen)

    def show_guest_booking_screen(self):
        self.stacked_widget.setCurrentWidget(self.guest_booking)

    def show_login_successful_message(self):
        QMessageBox.information(self, "Login", "Login Successful")
        self.show_dashboard_screen()
        self.login_screen.error.clear()

    def show_dashboard_screen(self):
        self.stacked_widget.setCurrentWidget(self.dashboard)

    def show_login_screen(self):
        self.stacked_widget.setCurrentWidget(self.login_screen)
        self.login_screen.username.clear()
        self.login_screen.password.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.setFixedSize(802, 600)
    main_widget.show()
    sys.exit(app.exec_())