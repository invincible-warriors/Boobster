import telegram.ext


class ControlModule:
    @staticmethod
    def add_module(application: telegram.ext.Application, module):
        handlers = module.get_handlers()
        application.add_handlers(handlers)
