#!/usr/bin/env python

import gym
import random
import numpy as np
import tflearn
import time
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from statistics import median, mean
from collections import Counter


LR = 0.002 #Learning rate can be tweeked accord to envi
env = gym.make("MsPacman-ram-v0")
env.reset()
goal_steps = 100 		#500 frames its balance the pole then it +1 to the score
score_requirement = 80  #Random games of score more than 50 > Learn
initial_games = 7500 	#If we increase it we brute force the learning(not req)

def some_random_games_first():
    # Each of these is its own game.
    for episode in range(10):
        env.reset()
        # this is each frame, up to 200...but we wont make it that far.
        for t in range(200): # 200 instead of goal step(500)
            # This will display the environment
            # Only display if you really want to see it.
            # Takes much longer to display it.
            env.render()
            time.sleep(.01)
            # This will just create a sample action in any environment.
            # In this environment, the action can be 0 or 1, which is left or right
            action = random.randrange(0,4)
            
            # this executes the environment with an action, 
            # and returns the observation of the environment, 
            # the reward, if the env is over, and other info.
            observation, reward, done, info = env.step(action)
            print(action)
            print(observation)
            print(reward)
            print(done)
            print(info)
            print('\n')
            if done == True:
                print("OKYOKYOKYOKYOKYOKY")
            if done:
                break
                
some_random_games_first()
'''
def initial_population():
    # [OBS, MOVES]
    # We append the data if the score is above 50 
    training_data = []  
    # all scores:
    scores = []
    # just the scores that met our threshold:
    accepted_scores = []
    # iterate through however many games we want:
    for _ in range(initial_games):
        score = 0
        # moves specifically from this environment:
        # stores all the movements, cauze we dont knw we won or not
        game_memory = []
        # previous observation that we saw
        prev_observation = []
        # for each frame in 200
        for _ in range(goal_steps):
            # choose random action (0 or 1)
            # for other game we can use > action = env.action_space.sample() by repalcing the below line
            action = random.randrange(0,4)
            # do it!
            observation, reward, done, info = env.step(action)
            
            # notice that the observation is returned FROM the action
            # so we'll store the previous observation here, pairing
            # the prev observation to the action we'll take.
            if len(prev_observation) > 0 :
                game_memory.append([prev_observation, action])
            prev_observation = observation
            score+=reward
            if done: break

        # IF our score is higher than our threshold, we'd like to save
        # every move we made
        # NOTE the reinforcement methodology here. 
        # all we're doing is reinforcing the score, we're not trying 
        # to influence the machine in any way as to HOW that score is 
        # reached.
        if score >= score_requirement:
            accepted_scores.append(score)
            for data in game_memory:
                # convert to one-hot (this is the output layer for our neural network)
                if data[1] == 3:
                    output = [0,0,0,1]
                elif data[1] == 2:
                    output = [0,0,1,0]
                elif data[1] == 1:
                    output = [0,1,0,0]
                elif data[1] == 0:
                    output = [1,0,0,0]
                    
                # saving our training data
                training_data.append([data[0], output])

        # reset env to play again
        env.reset()
        # save overall scores
        scores.append(score)
    
    # just in case you wanted to reference later
    training_data_save = np.array(training_data)
    np.save('saved.npy',training_data_save)
    
    # some stats here, to further illustrate the neural network magic!
    print('Average accepted score:',mean(accepted_scores))
    print('Median score for accepted scores:',median(accepted_scores))
    print(Counter(accepted_scores))
    
    return training_data

initial_population()

def neural_network_model(input_size):

    network = input_data(shape=[None, input_size, 1], name='input')

    network = fully_connected(network, 128, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 256, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 512, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 256, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 128, activation='relu')
    network = dropout(network, 0.8)

    #								output(1,0)
    network = fully_connected(network, 4, activation='softmax')
    network = regression(network, optimizer='adam', learning_rate=LR, loss='categorical_crossentropy', name='targets')
    model = tflearn.DNN(network, tensorboard_dir='log')

    return model


def train_model(training_data, model=False):
	# training data contains observ and the action we took (0,1) or (1,0)
	# X feature set of all the observ from the training data
	# Y feature set of all the action we took
    X = np.array([i[0] for i in training_data]).reshape(-1,len(training_data[0][0]),1)
    y = [i[1] for i in training_data]

    if not model:
        model = neural_network_model(input_size = len(X[0]))
    
    #										to much epoch we r gonna overfit the model
    model.fit({'input': X}, {'targets': y}, n_epoch=3, snapshot_step=500, show_metric=True, run_id='openai_learning')
    return model

training_data = initial_population()
model = train_model(training_data)

scores = []
choices = []
for each_game in range(50):
    score = 0
    game_memory = []
    prev_obs = []
    env.reset()
    for _ in range(goal_steps):
        env.render()

        if len(prev_obs)==0:
            action = random.randrange(0,4)
        else:
            action = np.argmax(model.predict(prev_obs.reshape(-1,len(prev_obs),1))[0])

        choices.append(action)
                
        new_observation, reward, done, info = env.step(action)
        prev_obs = new_observation
        game_memory.append([new_observation, action])
        score+=reward
        if done: break

    scores.append(score)

print('Average Score:',sum(scores)/len(scores))
print('choice 1:{}  choice 0:{}'.format(choices.count(1)/len(choices),choices.count(0)/len(choices)))
print(score_requirement)
'''
