# IEE
This project is aimed to calculate the IEE score for commercial living-stream vedio and fit the model to predict the product sales
## Step1
The first step is to align these three type files[vedio, audio and transcript] based on the timestamp in the transcript file.
## Step2
Uesing the casual model to calculate the ITE score of every feature of different modality in every time window, and then aggregate the ITE score to product IEE score and influencer IEE score.
## Step3
Fit a predictive model, the input is the product IEE score and influencerIEE score,
