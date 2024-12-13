import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class LinearQNet(nn.Module):
    def __init__(self, inputSize, hiddenSize1, hiddenSize2, outputSize):
        super(LinearQNet, self).__init__()
        self.fc1 = nn.Linear(inputSize, hiddenSize2)
        self.fc3 = nn.Linear(hiddenSize2, outputSize)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc3(x)
        return x


class QTrainer:

    def __init__(self, model, lr, gamma):
        self.model = model
        self.lr = lr
        self.gamma = gamma

        self.optimizer = optim.Adam(model.parameters(), self.lr)
        self.lossFunction = nn.MSELoss()

    def trainStep(self, state, action, reward, newState, done):

        stateTensor = torch.tensor(state, dtype=torch.float)
        actionTensor = torch.tensor(action, dtype=torch.long)
        rewardTensor = torch.tensor(reward, dtype=torch.float)
        newStateTensor = torch.tensor(newState, dtype=torch.float)

        if len(stateTensor.shape) == 1:
            stateTensor = torch.unsqueeze(stateTensor, 0)
            newStateTensor = torch.unsqueeze(newStateTensor, 0)
            actionTensor = torch.unsqueeze(actionTensor, 0)
            rewardTensor = torch.unsqueeze(rewardTensor, 0)
            done = (done, )

        prediction = self.model(stateTensor)

        target = prediction.clone()

        for i in range(len(done)):
            Qnew = rewardTensor[i]

            if not done[i]:
                Qnew = rewardTensor[i] + self.gamma * torch.max(self.model(newStateTensor[i]))

            target[i][torch.argmax(actionTensor[i]).item()] = Qnew # <- fix 3

        # print(f"State Tensor Shape: {stateTensor.shape}")
        # print(f"Action Tensor Shape: {actionTensor.shape}")
        # print(f"Reward Tensor Shape: {rewardTensor.shape}")
        # print(f"New State Tensor Shape: {newStateTensor.shape}")

        self.optimizer.zero_grad()
        loss = self.lossFunction(target, prediction)
        loss.backward()

        self.optimizer.step()
