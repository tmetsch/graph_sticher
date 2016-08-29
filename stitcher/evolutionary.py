"""
Implements stitching, validation and filtering functions based on
evolutionary algorithm.
"""

import logging
import random

LOG = logging.getLogger()


class Candidate(object):
    """
    A candidate of a population for an evolutionary algorithm
    """

    def __init__(self, gen):
        """
        Initialize the candidate.

        :param gen: The genetics of the candidate
        """
        self.gen = gen

    def fitness(self):
        """
        Calculate the fitness of this candidate based on it's genes.
        :return:
        """
        raise NotImplementedError('Not done yet.')

    def mutate(self):
        """
        Mutate the candidate.
        """
        raise NotImplementedError('Not done yet.')

    def crossover(self, partner):
        """
        Cross this candidate with another one.
        """
        raise NotImplementedError('Not done yet.')


class BasicEvolution(object):
    """
    Implements basic evolutionary behaviour.
    """

    def __init__(self, percent_cutoff=0.2, percent_diversity=0.1,
                 percent_mutate=0.1, growth=1.0):
        """
        Initialize.

        :param percent_cutoff: Which top percentage of the population survives.
        :param percent_diversity: Which percentage to randomly add from the
            unfit population portion - keeps diversity up.
        :param percent_mutate: Percentage of the new population which should
            mutate randomly.
        :param growth: growth percentage of the new population to indicate
            growth/shrinking.
        """
        self.cutoff = percent_cutoff
        self.diversity = percent_diversity
        self.mutate = percent_mutate
        self.growth = growth

    def _darwin(self, population):
        """
        Evolve the population - the strongest survive and some randomly picked
        will survive. A certain percentage will mutate.

        :param population: Population list sorted by fitness.
        :return: List of candidates
        """
        # best possible parents
        new_population = population[0:int(len(population) * self.cutoff)]
        div_pool = population[int(len(population) * self.cutoff):-1]

        # diversity - select some random from 'bad' pool
        for _ in range(int(self.diversity * len(div_pool))):
            i = random.randint(0, len(div_pool) - 1)
            new_population.append(div_pool[i])

        # mutate some
        for _ in range(int(self.mutate * len(new_population))):
            i = random.randint(0, len(new_population) - 1)
            new_population[i].mutate()

        # create children
        len_pop = len(population)
        len_new_pop = len(new_population)
        for _ in range(int(len_pop * self.growth) - len_new_pop):
            candidate1 = population[random.randint(0, len_new_pop - 1)]
            candidate2 = population[random.randint(0, len_new_pop - 1)]
            child = candidate1.crossover(candidate2)
            new_population.append(child)

        LOG.debug('New population length: ' + str(len(new_population)))
        return new_population

    def run(self, population, max_runs, fitness_goal=0.0, stabilizer=False):
        """
        Play the game of life.

        :param population: The initial population.
        :param max_runs: Maximum number of iterations.
        :param fitness_goal: Breakoff value for fitness - default 0.0
        :param stabilizer: If True iteration will break off after population
            stabilizes - comes with a slight performance penalty. Note: only
            useful when the population has a stable length (growth=1.0) :-).
        :return: Number of iterations used and the final population.
        """
        # evolve till max iter, 0.0 (goal) or all death
        iteration = 0
        fitness_sum = 0.0
        population.sort(key=lambda candidate: candidate.fitness())
        while iteration <= max_runs:
            LOG.debug('Iteration: ' + str(iteration))

            population = self._darwin(population)
            population.sort(key=lambda candidate: candidate.fitness())

            if population[0].fitness() == fitness_goal:
                LOG.info('Found solution in iteration: ' + str(iteration))
                break

            if stabilizer:
                new_fitness_sum = sum(candidate.fitness() for
                                      candidate in population)
                if new_fitness_sum == fitness_sum:
                    # in the last solution all died...
                    LOG.info('Population stabilized after iteration: ' +
                             str(iteration - 1))
                    break
                fitness_sum = new_fitness_sum

            iteration += 1

        # show results
        if iteration >= max_runs:
            LOG.warn('Maximum number of iterations reached')
        LOG.info('Final population: ' + repr(population))
        return iteration, population
