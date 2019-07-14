import gambit
import os
from cvxopt import matrix, solvers

def cvxtest(arr, numv):
	c = matrix(([0.0] * numv) + [-1])
	k = [[-arr[0][cvxi], -arr[1][cvxi]] for cvxi in xrange(len(arr[0]))]
	for cvxi in xrange(len(arr[0])):
		k[cvxi].extend([-int(cvxi == cvxj) for cvxj in xrange(numv)])
	k.append([1, 1] + ([0] * numv))
	G = matrix([[float(i) for i in k1] for k1 in k])
	h = matrix(([0.0] * len(k[0])))
	A = matrix([[1.0] for cvxj in xrange(numv)] + [[0.0]])
	b = matrix([1.0])
	sol = solvers.lp(c, G, h, A, b)
	return [float(xi) for xi in sol['x']][:-1]

def prob(a, numa, numb):
	p1 = [sum(a[i:i + numb]) for i in xrange(0, len(a), numb)]
	p2 = []
	for i in xrange(numb):
		s, si = 0, i
		while si < len(a):
			s = s + a[si]
			si = si + numb
		p2.append(s)
	return [i / sum(p1) for i in p1], [i / sum(p2) for i in p2]

def epayof(a, ki, kj):
	lki, lkj, e, e1 = len(ki), len(kj), 0, 0
	for i in xrange(len(a[0])):
		e = e + (a[0][i] * ki[i / lkj] * kj[i % lkj])
	for i in xrange(len(a[1])):
		e1 = e1 + (a[1][i] * ki[i / lkj] * kj[i % lkj]) 
	return e, e1

#Set variable actions and general game command s
sgame = 'java -jar gamut.jar -output GambitOutput -normalize -min_payoff 1 -max_payoff 1000 -g '
actions = [2, 10, 20, 30, 40, 60]
g1 = open('output.txt', 'w')
for au in actions:
	asw, bet, tg, werr, berr = 0, 0, 0, [], []
	#Generate RandomGame (Games 001 - 100)
	for i in xrange(1, 31):
		#Generate the game file to grab data from, grab the data, close the file
		t = ('0' * (3 - len(str(i)))) + str(i)
		os.system(sgame + 'RandomGame -players 2 -actions ' + str(au) + ' -f ' + t + '.nfg >/dev/null 2>&1')
		g = gambit.Game.read_game(t + '.nfg')
	
		#Put data into payoff matrices
		gamenum = i
		a1 = [[], []]
		for profile in g.contingencies:
			a1[0].append(float(g[profile][0]))
			a1[1].append(float(g[profile][1]))
		r = list(gambit.nash.lcp_solve(g, use_strategic=True, rational=False, stop_after=1)[0])
		r = [r[:au], r[au:]]
		ei, ej = epayof(a1, r[0], r[1])
		k = cvxtest(a1, au * au)
		ki, kj = prob(k, au, au)
		ei1, ej1 = epayof(a1, ki, kj)
		vi1 = int(ei1 >= ei)
		if ei1 >= ei:
			berr.append(abs((ei1 - ei) / ei))
		else:
			werr.append(abs((ei1 - ei) / ei))
		vi2 = int(ej1 >= ej)
		if ej1 >= ej:
			berr.append(abs((ej1 - ej) / ej))
		else:
			werr.append(abs((ej1 - ej) / ej))	
		asw = asw + int((vi1 + vi2) >= 1)
		bet = bet + int((vi1 + vi2) == 2)
	g1.write('Action:' + str(au) + '\n')
	g1.write('Num of games where MM do as well or better than LH:' + str(asw) + '\n')
	g1.write('Num of games where MM do strictly better than LH:' + str(bet) + '\n')
	g1.write('Mean relative error when MM does better than LH:' + str(sum(berr) / float(len(berr))) + '\n')
	g1.write('Mean relative error when MM does worse than LH:' + str(sum(werr) / float(len(werr))) + '\n')
	g1.write('\n')
g1.close()
