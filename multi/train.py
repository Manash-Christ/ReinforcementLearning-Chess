from agent import Agent
from environ import MultiplayerSnakeGameAI


scoresHistory = []
meanScores = []

def train():

    totalScore1 = 0
    totalScore2 = 0
    bestScore1 = 0
    bestScore2 = 0

    agent1 = Agent(player_id=1)
    agent2 = Agent(player_id=2)
    game = MultiplayerSnakeGameAI()

    while agent1.numberOfGames < 200:

        game.reset()

        # print(f"Debug: Starting Game {agent1.numberOfGames} - Player 1 head: {game.head1}, Player 2 head: {game.head2}")

        state1 = agent1.getState(game)
        state2 = agent2.getState(game)

        done = False
        while not done:
            action1 = agent1.getAction(state1)
            action2 = agent2.getAction(state2)

            (reward1, reward2), done, score1, score2 = game.playStep(action1, action2)

            newState1 = agent1.getState(game)
            newState2 = agent2.getState(game)

            agent1.trainShortMemory(state1, action1, reward1, newState1, done)
            agent2.trainShortMemory(state2, action2, reward2, newState2, done)

            agent1.remember(state1, action1, reward1, newState1, done)
            agent2.remember(state2, action2, reward2, newState2, done)

            state1 = newState1
            state2 = newState2
            
            if game.frameIteration > 200:
                done=True

        agent1.trainLongMemory()
        agent2.trainLongMemory()

        agent1.numberOfGames += 1
        agent2.numberOfGames += 1

        if score1 > bestScore1:
            bestScore1 = score1

        if score2 > bestScore2:
            bestScore2 = score2

        totalScore1 += score1
        totalScore2 += score2

        meanScore1 = totalScore1 / agent1.numberOfGames
        meanScore2 = totalScore2 / agent2.numberOfGames

        scoresHistory.append((score1, score2))
        meanScores.append((meanScore1, meanScore2))

        if score1 == bestScore1 or score2 == bestScore2 or agent1.numberOfGames % 10 == 0:
            print(f"Game {agent1.numberOfGames}:\nPlayer 1 Score = {score1}, Best = {bestScore1}, Mean = {meanScore1}\nPlayer 2 Score = {score2}, Best = {bestScore2}, Mean = {meanScore2}")

train()

import matplotlib.pyplot as plt

scoresHistory1, scoresHistory2 = zip(*scoresHistory)  
meanScores1, meanScores2 = zip(*meanScores)         

plt.plot(scoresHistory1, label="Player 1 Score")
plt.plot(meanScores1, label="Player 1 Mean Score")

plt.plot(scoresHistory2, label="Player 2 Score")
plt.plot(meanScores2, label="Player 2 Mean Score")

plt.legend(["Score", "Mean Score"])

plt.xlabel("Game Number")
plt.ylabel("Score")
plt.title("Player 1 and Player 2 Scores Over Time")


plt.savefig("Multi.png")
