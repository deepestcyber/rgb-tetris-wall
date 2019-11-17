To install as service, copy the script to the systemd service directory

	sudo cp rgb-tetris-wall.service /etc/systemd/system

Enable the service and use `service` as you would normally

	sudo systemctl enable rgb-tetris-wall
	sudo service rgb-tetris-wall start

Some shortcuts:

	sudo service rgb-tetris-wall start
	sudo service rgb-tetris-wall stop
	sudo service rgb-tetris-wall restart
