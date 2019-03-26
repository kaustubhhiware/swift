from ftplib import FTP
ftp = FTP()
ftp.connect("10.0.0.5", 5555)
ftp.login('user', '12345')
ftp.retrlines('LIST')

file = raw_input("Enter file to download: ")

out = './client_dir/' + file
with open(out, 'wb') as f:
    ftp.retrbinary('RETR ' + file, f.write)
