import os
import time
import inspect


def train(user_train_function, model, save_dir, model_type='rnn', framework='pytorch', *args, **kwargs):
    """
    A universal training wrapper function provided by flatpack.
    """
    os.makedirs(save_dir, exist_ok=True)

    # Accessing arguments
    epochs = kwargs.get('epochs', 10)
    batch_size = kwargs.get('batch_size', 32)

    print(f"🚀 Training {model_type} model with epochs: {epochs} and batch size: {batch_size}")

    # Initialize a timer
    start_time = time.time()

    # Check if the user's training function has a 'model' parameter
    params = inspect.signature(user_train_function).parameters
    if 'model' in params:
        # If so, call the function with the model object provided
        user_train_function(model=model, *args, **kwargs)
    else:
        # If not, call the function without the model object
        user_train_function(*args, **kwargs)

    # Calculate and display the total training time
    elapsed_time = time.time() - start_time
    print(f"✅ Training completed in {elapsed_time:.2f} seconds")

    # Save the trained model based on the specified framework
    if framework == 'pytorch':
        import torch
        torch.save(model.state_dict(), os.path.join(save_dir, f'{model_type}_model.pth'))

    return model
