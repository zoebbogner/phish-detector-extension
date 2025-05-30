from models.content.main import training as content_training, production as content_production
from models.url.main import training as url_training, production as url_production
from models.meta.main import training as meta_training, production as meta_production

def train_models():
    content_training()
    url_training()
    meta_training()

def save_models_for_production():
    content_production()
    url_production()
    meta_production()

if __name__ == "__main__":
    train_models()
    save_models_for_production()