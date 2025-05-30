from models.meta.model import train_meta_model_for_training, train_meta_model_for_production

def training():
    print("Training the meta model")
    train_meta_model_for_training()
    print("Meta model trained")

def production():
    print("Exporting the meta model for production")
    train_meta_model_for_production()
    print("Meta model exported")

if __name__ == "__main__":
    training()
    production()