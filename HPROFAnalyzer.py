import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import shutil
import subprocess
import os
from zipfile import ZipFile
import codecs
from bs4 import BeautifulSoup
import sys
def main():    
    # Set up the SMTP server details
    hprofname = r''+sys.argv[1]
    mat_path = r''+sys.argv[2] #Location of ParseHeapDump.bat in MAT installization
    projectpath = r''+sys.argv[3]
    recipient = r''+sys.argv[4]
    reportpath = projectpath + r'\MATReports'  #Location of HPROF files
    hprof_file_path = reportpath + hprofname
    success = run_mat_leak_suspect_report(mat_path, hprof_file_path)
    report = "_Leak_Suspects"
    zipfolder = reportpath + (hprofname[:hprofname.index(r".hprof")] + report + ".zip")
    outpath = projectpath + r'\out'
    if success:
        with ZipFile(zipfolder, 'r') as zip:
            zip.extractall(outpath)
        indexfile = outpath+ r"\index.html"
        tableofcontents = outpath+ r"\toc.html"
        
        f = codecs.open(indexfile, 'r', 'utf-8')
        leakreport = BeautifulSoup(f.read(), features="html.parser").get_text()
        hasMemoryLeak = False if ("No leak suspect was found") in leakreport else True
        if hasMemoryLeak:
            print("Memory leak detected - sending alert...")
            #suspectlist = outpath + r"\pages\18.html"
            g = codecs.open(indexfile, 'r', 'utf-8')
            overview = BeautifulSoup(g.read(), features="html.parser").get_text()
            overview = overview[overview.index("Problem Suspect"):overview.index("Created by Eclipse Memory Analyzer")-18]       
            overview = overview[:17] +'\n' + overview[17:]
            #Set up Email
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587  # For Gmail, use port 587
            sender_email = r'mailcodetester887@gmail.com'
            sender_password = r'uzlgbvesgpcneoue'
            sendmail(smtp_server, smtp_port, sender_email, sender_password, tableofcontents, overview, recipient)
        else:
            print("No memory leak suspect was found")
def sendmail(smtp_server, smtp_port, sender_email, sender_password, toc, overview, recipient):
    # Compose the email
    subject = 'Memory Leak Found'
    message = 'A leak has been detected.\n\n' + overview

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    # Establish a secure connection with the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print('Email sent successfully!')

def run_mat_leak_suspect_report(mat_path, hprof_file_path):
    # Command to generate leak suspect report
    command = [
        mat_path,
        hprof_file_path,
        "-output=.html",
        "-redact=BASIC",
        "org.eclipse.mat.api:suspects"        
    ]
    try:
        # Execute the command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode == 0:
            print("Leak suspect report generated successfully.")
            return True
        else:
            print("Error generating leak suspect report:", error)
            return False
    except subprocess.CalledProcessError as e:
        print("Error generating leak suspect report:", e)
        return False
main()
# Example usage

#   cd C:\\MyProj\\Deltek2023\\EclipseMATAutoEmail
#   MemoryLeakAlertSystem.bat <pid> <ParseHeapDump.bat location> <project folder> <recipient email address>

#   cd C:\\MyProj\\Deltek2023\\EclipseMATAutoEmail
#   MemoryLeakAlertSystem.bat 42560 C:\\Users\\mwang\\eclipse\\java-2022-06\\eclipse\\plugins\\mat\\ParseHeapDump.bat C:\\MyProj\\Deltek2023\\EclipseMATAutoEmail mailcodereceiver@gmail.com
