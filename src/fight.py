import asyncio

from enum import Enum, auto
from random import choice
from re import A

class Action(Enum):
    HIGHKICK = auto()
    LOWKICK = auto()
    HIGHBLOCK = auto()
    LOWBLOCK = auto()

class Agent:
    def __aiter__(self, health=5):
        self.health = health
        self.actions = list(Action)
        return self

    async def __anext__(self):
        return choice(self.actions)

def take_action_to_neo(action):
    return Action.LOWKICK if action == Action.HIGHBLOCK else \
           Action.HIGHKICK if action == Action.LOWBLOCK else \
           Action.HIGHBLOCK if action == Action.HIGHKICK else \
           Action.LOWBLOCK

def check_damage(action):
    return action == Action.LOWKICK or action == Action.HIGHKICK

async def print_resul_fight(action, agent):
    if agent.health > 0:
        action_neo = take_action_to_neo(action)
        if check_damage(action_neo):
            agent.health -= 1
        print(f"Agent: {action}, Neo: {action_neo}, Agent Health: {agent.health}")
        
async def fight(agent):
    async for action in agent:
        tasc = asyncio.create_task(print_resul_fight(action, agent))
        if agent.health < 1:
            print("Neo wins!")
            break
        else:
            await tasc
    
async def print_resul_fight_to_many(action, agent, counter):
    if agent.health > 0:
        action_neo = take_action_to_neo(action)
        if check_damage(action_neo):
            agent.health -= 1
        print(f"Agent {counter}: {action}, Neo: {action_neo}, Agent {counter} Health: {agent.health}")

async def fight_to_many(agent, counter):
    async for action in agent:
        tasc = asyncio.create_task(print_resul_fight_to_many(action, agent, counter))
        if agent.health < 1:
            break
        else:
            await tasc

async def fightmany(agents):
    counter = 1
    tascs = []
    for agent in agents:
        tascs.append(asyncio.create_task(fight_to_many(agent, counter)))
        counter += 1
    for tasc in tascs:
        await tasc
    print("Neo wins!")

def main(n):
    if n == 1:
        agent = Agent()
        asyncio.run(fight(agent))
    elif n > 1:
        agents = [Agent() for _ in range(n)]
        asyncio.run(fightmany(agents))
        
if __name__ == "__main__":
    agent = Agent()
    main(3)