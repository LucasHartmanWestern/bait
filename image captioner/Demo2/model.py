import torch
import torch.nn as nn
import torchvision.models as models
import torch.nn.functional as F
from torchvision.models import inception_v3, Inception_V3_Weights

# CNN Encoder using InceptionV3 for image feature extraction
class EncoderCNN(nn.Module):
    def __init__(self, embed_size, train_CNN=False):
        super(EncoderCNN, self).__init__()
        self.train_CNN = train_CNN
        self.inception = inception_v3(weights=Inception_V3_Weights.IMAGENET1K_V1, aux_logits=True)
        self.inception.fc = nn.Linear(self.inception.fc.in_features, embed_size)
        self.relu = nn.ReLU()
        # Previously 0.5
        self.dropout = nn.Dropout(0.3)

    def forward(self, images):
        # Forward pass for images, training vs eval mode
        if self.training:
            outputs = self.inception(images)
            features = outputs.logits  
        else:
            # In evaluation mode, it directly returns the main output tensor
            features = self.inception(images)
        
        features = self.relu(features)
        return self.dropout(features)

# Defines RNN decoder for generating captions from image features 
class DecoderRNN(nn.Module):
    def __init__(self, embed_size, hidden_size, vocab_size, num_layers):
        super(DecoderRNN, self).__init__()
        self.embed = nn.Embedding(vocab_size, embed_size)
        self.lstm = nn.LSTM(embed_size, hidden_size, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, vocab_size)
        # Previously 0.5
        self.dropout = nn.Dropout(0.3)

    # Predict next word using outputs of LSTM
    def forward(self, features, captions):
        embeddings = self.embed(captions)  
        # LSTM processing
        hiddens, _ = self.lstm(embeddings)  # Here you might consider how to incorporate features, but not by direct concatenation with embeddings
        outputs = self.linear(hiddens)
        return outputs
    
# Combines CNN and RNN for a comprehensive model
class CNNtoRNN(nn.Module):
    def __init__(self, embed_size, hidden_size, vocab_size, num_layers):
        super(CNNtoRNN, self).__init__()
        self.encoderCNN = EncoderCNN(embed_size)
        self.decoderRNN = DecoderRNN(embed_size, hidden_size, vocab_size, num_layers)

    # Gets features and captions
    def forward(self, images, captions):
        features = self.encoderCNN(images)
        outputs = self.decoderRNN(features, captions)
        return outputs
    
    # Generates the caption for the image
    def caption_image(self, image, vocabulary, max_length=50):
        result_caption = []

        with torch.no_grad():
            x = self.encoderCNN(image).unsqueeze(0)  
            states = None  

            for _ in range(max_length):
                hiddens, states = self.decoderRNN.lstm(x, states)  
                output = self.decoderRNN.linear(hiddens.squeeze(0)) 
                predicted = output.argmax(1)  
                result_caption.append(predicted.item())
                x = self.decoderRNN.embed(predicted).unsqueeze(0)  

                if vocabulary.itos[predicted.item()] == "<EOS>":
                    break

        return [vocabulary.itos[idx] for idx in result_caption]

class CustomLoss(nn.Module):
    def __init__(self, pad_idx, unk_idx, unk_penalty_lambda=1.0):
        super().__init__()
        self.pad_idx = pad_idx
        self.unk_idx = unk_idx
        self.unk_penalty_lambda = unk_penalty_lambda
    
    def forward(self, outputs, targets):
        # Calculate the standard cross entropy loss
        loss = F.cross_entropy(outputs.view(-1, outputs.size(-1)), targets.view(-1), ignore_index=self.pad_idx, reduction='none')
        
        # Calculate a mask of where unk tokens are in the targets
        unk_mask = (targets.view(-1) == self.unk_idx).float()
        
        # Apply the penalty to the loss where unk tokens are
        loss += self.unk_penalty_lambda * unk_mask * loss
        
        # Return the mean loss
        return loss.mean()