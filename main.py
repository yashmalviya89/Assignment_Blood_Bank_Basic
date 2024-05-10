import csv
import os
import re
from datetime import datetime, timedelta

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


#  email credentials
EMAIL_HOST = "smtp.gmail.com"  # smtp-mail.outlook.com for outlook
EMAIL_PORT = 587
EMAIL_USERNAME = "yashum0089@gmail.com"
EMAIL_PASSWORD = "slbzylranpbeugol"


def send_email(subject, message, to_email):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USERNAME
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print("Failed to send email:", str(e))


# Function to add a new donor to the CSV file
def add_donor(name, blood_group, contact_number, email):
    # Validate phone number format using regular expression
    if not re.match(r"^\d{10}$", contact_number):
        print(
            "Invalid phone number format. Please enter a 10-digit number without any spaces or special characters."
        )
        return

    # Validate blood group type
    valid_blood_groups = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
    if blood_group not in valid_blood_groups:
        print(
            "Invalid blood group. Please enter a valid blood group type (e.g., A+, B-, O-, AB+)."
        )
        return

    # If both phone number and blood group are valid, proceed to add the donor
    with open("donornew.csv", "a", newline="") as csvfile:
        fieldnames = ["Name", "Blood Group", "Contact Number"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Check if the file is empty, if so, write the header
        if csvfile.tell() == 0:
            writer.writeheader()

        # Write the details of the new donor
        writer.writerow(
            {"Name": name, "Blood Group": blood_group, "Contact Number": contact_number}
        )
    print("Thank you for registering as a donor!")
    send_email(
        "Welcome to BloodBank",
        "Thank you for registering as a donor!",
        email,
    )


# Function to add a new blood donation camp to the CSV file
def add_blood_donation_camp(
    state, district, date, time, camp_name, address, contact, conducted_by
):
    headers = [
        "State",
        "District",
        "Date",
        "Time",
        "Camp Name",
        "Address",
        "Contact",
        "Conducted By",
    ]
    data = {
        "State": state,
        "District": district,
        "Date": date.strftime("%Y-%m-%d"),
        "Time": time,
        "Camp Name": camp_name,
        "Address": address,
        "Contact": contact,
        "Conducted By": conducted_by,
    }

    if not os.path.exists("blood_donation_camps.csv"):
        with open("blood_donation_camps.csv", "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerow(data)
    else:
        with open("blood_donation_camps.csv", "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writerow(data)
    print("Blood donation camp added successfully!")


def search_blood_donation_camps(state=None, district=None):
    camps = []
    with open("blood_donation_camps.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if (state is None or row["State"].lower() == state.lower()) and (
                district is None or row["District"].lower() == district.lower()
            ):
                camps.append(row)

    if camps:
        print("Upcoming Blood Donation Camps:")
        for camp in camps:
            print(
                f"State: {camp['State']}, District: {camp['District']}, Date: {camp['Date']}, Camp Name: {camp['Camp Name']}, Address: {camp['Address']}, Contact: {camp['Contact']}, Conducted By: {camp['Conducted By']}"
            )

    else:
        print("No upcoming blood donation camps found matching the criteria.")


# Function to find donors by blood group
def find_donor_by_blood_group(blood_group):
    matching_donors = []
    with open("donornew.csv", "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["Blood Group"] == blood_group:
                matching_donors.append(row)
    return matching_donors


# Function to delete a donor from the CSV file
def delete_donor(name):
    rows = []
    with open("donornew.csv", "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["Name"] != name:
                rows.append(row)

    with open("donornew.csv", "w", newline="") as csvfile:
        fieldnames = ["Name", "Blood Group", "Contact Number"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print("Donor deleted successfully.")


# Function to update donor details in the CSV file
def update_donor(name, contact_number):
    rows = []
    with open("donornew.csv", "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["Name"] == name:
                row["Contact Number"] = contact_number
            rows.append(row)

    with open("donornew.csv", "w", newline="") as csvfile:
        fieldnames = ["Name", "Blood Group", "Contact Number"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print("Donor details updated successfully.")


# Function to view donor data from CSV file
def view_csv_file():
    if os.path.exists("donornew.csv"):
        with open("donornew.csv", "r", newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                print(", ".join(row))
    else:
        print("No donor data available.")


# Function to export donor data to PDF
def export_to_pdf():
    donors = []
    if os.path.exists("donornew.csv"):
        with open("donornew.csv", "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                donors.append([row["Name"], row["Blood Group"], row["Contact Number"]])

    if donors:
        pdf_filename = "donor_list.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
        table_data = [["Name", "Blood Group", "Contact Number"]] + donors
        table = Table(table_data)

        # Add style to table
        style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
        table.setStyle(style)

        # Add table to document
        doc.build([table])

        print("PDF created successfully:", pdf_filename)
    else:
        print("No donor data available.")


# Free health checkup


def add_hospital(name, address, contact, available_dates):
    headers = ["Name", "Address", "Contact", "Available Dates", "Slots"]

    # Generate available slots from 9 AM to 1 PM with 30-minute intervals
    slots = []
    start_time = datetime.strptime("09:00 AM", "%I:%M %p")
    end_time = datetime.strptime("01:00 PM", "%I:%M %p")
    current_time = start_time
    while current_time < end_time:
        slot_str = f"{current_time.strftime('%I:%M %p')} - {(current_time + timedelta(minutes=30)).strftime('%I:%M %p')}"
        slots.append(slot_str)
        current_time += timedelta(minutes=30)

    data = {
        "Name": name,
        "Address": address,
        "Contact": contact,
        "Available Dates": ",".join(available_dates),
        "Slots": ",".join(slots),
    }

    if not os.path.exists("hospitals.csv"):
        with open("hospitals.csv", "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerow(data)
    else:
        with open("hospitals.csv", "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writerow(data)
    print("Hospital added successfully!")


def book_appointment(hospital_name, donor_name, donor_email):
    with open("hospitals.csv", "r+", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        hospitals = list(reader)
        fieldnames = reader.fieldnames or []  # Use empty list if fieldnames is None
        for hospital in hospitals:
            if hospital["Name"] == hospital_name:
                available_dates = hospital["Available Dates"].split(",")
                appointment_date = available_dates[
                    0
                ]  # Automatically select the first available date
                available_slots = hospital["Slots"].split(",")
                print("Available Slots on date", appointment_date)
                for i, slot in enumerate(available_slots, start=1):
                    print(f"{i}. {slot}")
                slot_index = int(input("Enter slot number to book: ")) - 1
                if 0 <= slot_index < len(available_slots):
                    selected_slot = available_slots[slot_index]
                    print("Selected Slot:", selected_slot)
                    available_slots.remove(selected_slot)
                    hospital["Slots"] = ",".join(available_slots)
                    # Update the row in the CSV file
                    with open("hospitals.csv", "w", newline="") as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(hospitals)
                    # Store the booked appointment in appointments.csv
                    appointment_data = {
                        "Hospital Name": hospital_name,
                        "Donor Name": donor_name,
                        "Donor Email": donor_email,
                        "Appointment Date": appointment_date,
                        "Slot": selected_slot,
                    }
                    # Check if appointments.csv exists, if not, create it and write headers
                    if not os.path.exists("appointments.csv"):
                        with open("appointments.csv", "w", newline="") as app_file:
                            fieldnames = [
                                "Hospital Name",
                                "Donor Name",
                                "Donor Email",
                                "Appointment Date",
                                "Slot",
                            ]
                            app_writer = csv.DictWriter(app_file, fieldnames=fieldnames)
                            app_writer.writeheader()
                            app_writer.writerow(appointment_data)
                    else:
                        # Append appointment to existing appointments.csv
                        with open("appointments.csv", "a", newline="") as app_file:
                            fieldnames = [
                                "Hospital Name",
                                "Donor Name",
                                "Donor Email",
                                "Appointment Date",
                                "Slot",
                            ]
                            app_writer = csv.DictWriter(app_file, fieldnames=fieldnames)
                            app_writer.writerow(appointment_data)
                    # Sending email notification to the donor
                    hospital_address = hospital["Address"]
                    hospital_contact = hospital["Contact"]
                    subject = "Appointment Confirmation"
                    message = f"Dear {donor_name},\n\nCongratulations! Your appointment at {hospital_name} has been successfully booked.\n\nHospital Name: {hospital_name}\nAddress: {hospital_address}\nSlot Timing: {selected_slot}\nAppointment Date: {appointment_date}\nContact: {hospital_contact}\n\nThank you for choosing our services.\n\nBest regards,\nBlood Bank Team"
                    send_email(subject, message, donor_email)
                    print(
                        "Appointment booked successfully! An email has been sent to the donor."
                    )
                    return
                else:
                    print("Invalid slot number.")
                    return
        print("Hospital not found in records.")


def cancel_appointment(hospital_name, donor_name):
    # Load appointments from CSV
    with open("appointments.csv", "r", newline="") as app_file:
        reader = csv.DictReader(app_file)
        appointments = list(reader)

    # Find the appointment to cancel
    for appointment in appointments:
        if (
            appointment["Hospital Name"] == hospital_name
            and appointment["Donor Name"] == donor_name
        ):
            # Remove appointment from the list
            appointments.remove(appointment)
            # Rewrite the updated list to the CSV file
            with open("appointments.csv", "w", newline="") as app_file:
                fieldnames = [
                    "Hospital Name",
                    "Donor Name",
                    "Donor Email",
                    "Appointment Date",
                    "Slot",
                ]
                writer = csv.DictWriter(app_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(appointments)

            # Load hospitals from CSV
            with open("hospitals.csv", "r", newline="") as hospital_file:
                reader = csv.DictReader(hospital_file)
                hospitals = list(reader)

            # Find the hospital
            for hospital in hospitals:
                if hospital["Name"] == hospital_name:
                    # Add the cancelled slot back to available slots
                    cancelled_slot = appointment["Slot"]
                    hospital["Slots"] += "," + cancelled_slot
                    # Rewrite the updated list to the CSV file
                    with open("hospitals.csv", "w", newline="") as hospital_file:
                        fieldnames = [
                            "Name",
                            "Address",
                            "Contact",
                            "Available Dates",
                            "Slots",
                        ]
                        writer = csv.DictWriter(hospital_file, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(hospitals)
                    break

            # Send cancellation email to donor
            donor_email = appointment["Donor Email"]
            subject = "Appointment Cancellation"
            message = f"Dear {donor_name},\n\nYour appointment at {hospital_name} has been successfully cancelled.\n\nWe apologize for any inconvenience caused. Please feel free to contact us if you need to reschedule or have any questions.\n\nBest regards,\nBlood Bank Team"
            send_email(subject, message, donor_email)
            print("Appointment cancelled successfully!")
            return
    print("Appointment not found.")


# Main function


def main():
    while True:
        print("Press 1. Register as Blood Donor")
        print("Press 2. Search for Donors by Blood Group")
        print("Press 3. View Donor Data from CSV File")
        print("Press 4. Export Donor Data to PDF")
        print("Press 5. Delete Donor")
        print("Press 6. Update Donor Details")
        print("Press 7. Add Blood Donation Camp")
        print("Press 8. Search for Blood Donation Camps")
        print("Press 9. Add hospitals to health checkup")
        print("Press 10. Book an Appointment for free health checkup")
        print("Press 11. Cancel Appointment")
        print("Press 0. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter your name: ")
            blood_group = input("Enter your blood group: ")
            contact_number = input("Enter your contact number: ")
            email = input("Enter your email address: ")
            add_donor(name, blood_group, contact_number, email)
        elif choice == "2":
            blood_group = input("Enter the required blood group: ")
            matching_donors = find_donor_by_blood_group(blood_group)
            if matching_donors:
                print("Matching donors found:")
                for donor in matching_donors:
                    print(f"Name: {donor['Name']}, Contact: {donor['Contact Number']}")
            else:
                print("No matching donors found.")
        elif choice == "3":
            print("Donor Data from CSV File:")
            view_csv_file()
        if choice == "4":
            print("Exporting Donor Data to PDF...")
            export_to_pdf()
        elif choice == "5":
            name = input("Enter the name of the donor to delete: ")
            delete_donor(name)
        elif choice == "6":
            name = input("Enter the name of the donor to update: ")
            contact_number = input("Enter the new contact number: ")
            update_donor(name, contact_number)
        elif choice == "7":
            state = input("Enter state: ")
            camp_name = input("Enter Camp Name: ")
            address = input("Enter Address of Camp: ")
            district = input("Enter district: ")
            contact = int(input("Enter Contact Number: "))
            conducted_by = input("Camp Conducted by: ")
            date_str = input("Enter date (YYYY-MM-DD): ")
            time_str = input("Enter time (HH:MM AM/PM): ")
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                add_blood_donation_camp(
                    state,
                    district,
                    date,
                    time_str,
                    camp_name,
                    address,
                    contact,
                    conducted_by,
                )
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")

        elif choice == "8":
            state = input("Enter state: ")
            district = input("Enter district: ")
            search_blood_donation_camps(state, district)

        elif choice == "9":
            name = input("Enter hospital name: ")
            address = input("Enter hospital address: ")
            contact = input("Enter hospital contact number: ")
            available_dates = input(
                "Enter available appointment date (YYYY-MM-DD): "
            ).split(",")
            add_hospital(name, address, contact, available_dates)
        elif choice == "10":
            hospital_name = input("Enter hospital name: ")
            donor_name = input("Enter your name: ")
            donor_email = input("Enter your email address: ")
            book_appointment(hospital_name, donor_name, donor_email)

        elif choice == "11":
            # Cancel Appointment
            hospital_name = input("Enter hospital name: ")
            donor_name = input("Enter donor name: ")
            cancel_appointment(hospital_name, donor_name)

        elif choice == "0":
            print("Exiting the blood bank application.")
            break
        else:
            print("Invalid choice. Please choose a valid option.")


if __name__ == "__main__":
    main()
