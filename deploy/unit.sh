curl -X PUT --data-binary @app.json --unix-socket \
       /var/run/control.unit.sock http://localhost/config/applications/ips_django

curl -X PUT --data-binary @routes.json --unix-socket \
       /var/run/control.unit.sock http://localhost/config/routes/ips

curl -X PUT --data-binary @listener.json --unix-socket \
       /var/run/control.unit.sock http://localhost/config/listeners/*:82