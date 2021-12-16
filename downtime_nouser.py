#!/bin/downtime.py
import os
import sys
import socket
import datetime
import time
import smtplib
import ssl
import urllib.request

FILE = os.path.join(os.getcwd(), "networkinfo.log")

def get_extip():
    # get my external/public IP address
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    return(external_ip)

def send_mail(str_failed,str_reconnect,str_downtime):
    # send an e-mail each time there is a reconnection
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com" # you can change this to youe preferred SMTP server domain name
    sender_email = "xxxxx@gmail.com"  # Enter your e-mail address. Must be valid in your SMTP server.
    receiver_email = "xxxxx@gmail.com"  # Enter receiver address
    password = "<you smtp server password, usually your e-mail password>"
    
    from email.message import EmailMessage
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = '(your ISP name) downtime notification'
    msg_Body = "<table border=""1""><caption><b>(your ISP name) downtime events</b><hr><b>IP address: </b>"+ \
                get_extip()+"</caption><tr><th><b>Event</b></th><th><b>Time</b></th></tr><tr><td>Disconnection:</td><td>"+ \
                str_failed+"</td></tr><tr><td>Reconnection:</td><td>"+ \
                str_reconnect+"</td></tr><tr><td>Down time:</td><td>"+ \
                str_downtime+"</td></tr></table>"
    msg.add_alternative(msg_Body, subtype='html')

    context = ssl.create_default_context()
    
    try:
        with smtplib.SMTP_SSL(smtp_server, port,context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    
    except smtplib.SMTPHeloError:
            print ("The server didn't reply properly to the HELO greeting.")
    except smtplib.SMTPAuthenticationError:
            print ("The server The server didn't accept the username/password combination.")
    except smtplib.SMTPNotSupportedError:
            print ("The AUTH command is not supported by the server.")
    except smtplib.SMTPException:
            print ("No suitable authentication method was found.")
    except smtplib.SMTPHeloError:
            print ("The server didn't reply properly to the HELO greeting.")
    except smtplib.SMTPRecipientsRefused:
            print ("The server rejected ALL recipients (no e-mail sent).")
    except smtplib.SMTPSenderRefused:
            print ("The server didn't accept the from_addr.")
    except smtplib.SMTPDataError:
            print ("The server replied with an unexpected error code (other than a refusal of a recipient).")
    except smtplib.SMTPNotSupportedError:
            print("The mail_options parameter includes 'SMTPUTF8' but the SMTPUTF8 extension is not supported by the server.")
    except Exception:
        print("e-mail sent successfully!")
        server.quit

def ping():
    
    # to ping a particular PORT at an IP (in this case the DNS port in my external interface)
    # if the machine won't receive any packets from
    # the server for more than 5 seconds
    # i.e no connection is
    # made(machine doesn't have a live internet connection)
    # <except> part will be executed
    try:
        socket.setdefaulttimeout(3)
  
        # AF_INET: address family (IPv4)
        # SOCK_STREAM: type for TCP (PORT)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          
        #set host to your external IP address. If you use another address and its down it may report a false positive.
        host = get_extip()
        port = 53
  
        server_address = (host, port)
          
        # send connection request to the defined server
        s.connect(server_address)
  
    except OSError as error:
        
        # function returning false after
        # data interruption(no connection)
        return False
    else:
        
        # the connection is closed after
        # machine being connected
        s.close()
        return True

def calculate_time(start, stop):
	
	# to calculate unavailability time
	difference = stop - start
	seconds = float(str(difference.total_seconds()))
	return str(datetime.timedelta(seconds=seconds)).split(".")[0]

def first_check():
    # to check if the machine already have a live internet connection
  
    # if ping returns true
    if ping():
        live = "\nCONNECTION ACQUIRED\n"
        print(live)
        connection_acquired_time = datetime.datetime.now()
        acquiring_message = "connection acquired at: " + \
            str(connection_acquired_time).split(".")[0]
        print(acquiring_message)
  
        # writes into the log file
        with open(FILE, "a") as file:
            file.write(live)
            file.write(acquiring_message + "\n")
        return True
  
    # if ping returns false
    else:
        not_live = "\nCONNECTION NOT ACQUIRED\n"
        print(not_live)
  
        # writes into the log file
        with open(FILE, "a") as file:
            file.write(not_live + "\n")
        return False

def main():
    # MAIN
    monitor_start_time = datetime.datetime.now()
      
    # monitoring time is when the script
    # started monitoring internet connection status
    monitoring_date_time = "monitoring started at: " + \
        str(monitor_start_time).split(".")[0]
  
    if first_check():
        # if true
        print(monitoring_date_time)
          
        # monitoring will only start when
        # the connection will be acquired
  
    else:
        # if false
        while True:
            
            # infinite loop to check if the connection is acquired
            # will run until there is a live internet connection
            if not ping():
                
                # if connection not acquired
                time.sleep(1)
            else:
                
                # if connection is acquired
                first_check()
                print(monitoring_date_time)
                break
  
            with open(FILE, "a") as file:
                # writes into the log file
                file.write("\n")
                file.write(monitoring_date_time + "\n")
  
    while True:
        
        # FIRST WHILE, infinite loop,
        # will run until the machine is on
        # or the script is manually terminated
        if ping():
            # if true: the loop will execute after every 5 seconds
            time.sleep(5)
  
        else:
            
            # if false: fail message will be displayed
            down_time = datetime.datetime.now()
            fail_msg = "disconnected at: " + str(down_time).split(".")[0]
            print(fail_msg)
  
            with open(FILE, "a") as file:
                # writes into the log file
                file.write(fail_msg + "\n")
  
            while not ping():
                # infinite loop,
                # will run till ping() return true
                time.sleep(1)
  
            up_time = datetime.datetime.now()
              
            # will execute after while true is
            # false (connection restored)
            uptime_message = "connected again: " + str(up_time).split(".")[0]
  
            total_down_time = calculate_time(down_time, up_time)
              
            # calling time calculating
            # function, printing down time
            unavailablity_time = "connection was unavailable for: " + total_down_time
  
            print(uptime_message)
            print(unavailablity_time)
  
            with open(FILE, "a") as file:
                  
                # log entry for connected restoration time,
                # and unavailability time
                file.write(uptime_message + "\n")
                file.write(unavailablity_time + "\n")

            m_downtime = down_time.strftime("%D %H:%M:%S")
            m_uptime = up_time.strftime("%D %H:%M:%S")
            m_elapsed = total_down_time

            send_mail(m_downtime,m_uptime,m_elapsed)

if __name__ == '__main__':
    main()
