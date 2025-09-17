from typing import List

class Subject:

    def __init__(self):

        self._observers: List = []

    def attach(self, observer):

        if observer not in self._observers:

            self._observers.append(observer)

    def detach(self, observer):

        try:

            self._observers.remove(observer)

        except ValueError:

            pass

    def notify(self, *args, **kwargs):

        for obs in list(self._observers):

            try:

                obs.update(self, *args, **kwargs)

            except Exception:

                pass

class Observer:

    def update(self, subject, *args, **kwargs):

        raise NotImplementedError("O metodo 'update' deve ser implementado pela subclasse.")

