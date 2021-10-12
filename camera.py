import subprocess,time,sys
while(True):
  # os.system('python3 /home/pi/Desktop/pi.py')
  p = subprocess.Popen('python3 /home/pi/Desktop/pi.py', stdin = sys.stdin,stdout = sys.stdout, stderr = sys.stderr, shell = True)
  print('haha')
  time.sleep(300)
  p.kill()
  print('hehe')