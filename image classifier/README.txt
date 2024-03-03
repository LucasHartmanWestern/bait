===== Instructions to setup ====

1. Import requirements

To do this step, open the terminal.
Once the terminal is open, type the following command:
cd 'image classifier'
Now that you are in the image classifier directory, type the following command:
pip install -r requirements.txt

===== Instructions to use ====

2. Get data

To get the training data, ensure you first have data in the 'data/unformatted' directory.
Once you have images, first run the formatter file by typing the following command:
py formatter.py
If you want to add noise to the dataset to improve generalization, also type the following:
py data_augmentor.py
You should now see images in the 'image classifier/data/augmented' directory.

3. Begin training

To begin training, simply type the following command:
py model_generator.py

4. Make predictions

To make new predictions, simply import the get_prediction() function from the app.py file.
Pass an image bytestream into this function as the only parameter, and the result will be in the following format:
('Hardware Title', 'Status of Lights')
A demo can be seen by running the following command:
py app.py
This will make a prediction on any image at the location 'data/predict_this.png'.