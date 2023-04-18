from twilio.rest import Client
from threading import Thread


class SMS(Thread):
    def __init__(self, location, direction):
        super().__init__()
        self.id = 'ACb89cbf8b26ea01d557870be5c19183af'
        self.auth = '1b65c7d1940ab12f2c923feed83b3aed'
        self.daemon = True
        self.location = location
        self.direction = direction
        self.client = Client(self.id, self.auth)

    def run(self):
        self.send()

    def run_once(f):
        def wrapper(*args, **kwargs):
            if not wrapper.has_run:
                wrapper.has_run = True
                return f(*args, **kwargs)
        wrapper.has_run = False
        return wrapper

    @run_once
    def send(self, num = '6303523796'):
        self.text = f"Drone detected at {self.location}\nIts direction is {self.direction}"
        try:
            self.msg = self.client.messages \
                .create(
                    body=self.text,
                    from_='+18582992819',
                    to='+91' + num
                )
            print(f'{self.msg.sid}')
        except Exception as e:
            print(f"{e}: SMS class")
            pass


SMS('Webcam', 'Stationary').start()
