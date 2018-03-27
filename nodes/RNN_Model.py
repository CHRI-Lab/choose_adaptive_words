import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import os


#nb_points_letter = 381
nb_class = 37
batch_size = 180
epoch = 100

# max_length = 381
nb_features = 6
lstm_size = 100
nn_size = 40



class Model():

	def __init__(self, max_length):

		self.session = tf.Session()
		self.save_dir = 'checkpoints/'
		self.max_length = max_length

		# if directory to save variable do not exist, create it
		if not os.path.exists(self.save_dir):
			os.makedirs(self.save_dir)

		# to save valu training and testing
		self.accuracy_training = []
		self.accuracy_testing = []

		# inputs
		self.seqlen = tf.placeholder(tf.int32, [None])
		self.data = tf.placeholder(tf.float32, [None, self.max_length, nb_features])
		self.label = tf.placeholder(tf.float32, [None, nb_class])
		self.dropout_keep_prob = tf.placeholder(tf.float32)
		self.batch_size = tf.placeholder(tf.int32)



		self.cell = tf.contrib.rnn.LSTMCell(lstm_size, state_is_tuple=True)
		self.stacked_lstm = tf.contrib.rnn.MultiRNNCell([self.cell] * 2, state_is_tuple=True)
		stacked_rnn = []
		for iiLyr in range(2):
			stacked_rnn.append(tf.nn.rnn_cell.LSTMCell(num_units=lstm_size, state_is_tuple=True))
		self.stacked_lstm = tf.nn.rnn_cell.MultiRNNCell(cells=stacked_rnn, state_is_tuple=True)
		self.val, self.state = tf.nn.dynamic_rnn(self.stacked_lstm, self.data, dtype=tf.float32, sequence_length=self.seqlen)


		# Start indices for each sample
		idx = tf.range(0, self.batch_size) * self.max_length + (self.seqlen - 1)
		self.last = tf.gather(tf.reshape(self.val, [-1, lstm_size]), idx)


		self.weight_1 = tf.Variable(tf.truncated_normal([lstm_size, nn_size]))
		self.bias_1 = tf.Variable(tf.constant(0.1, shape=[nn_size]))
		self.prediction_1 = tf.matmul(self.last, self.weight_1) + self.bias_1

		# relu
		self.prediction_1 = tf.nn.relu(self.prediction_1)
		# dropout 50%
		self.prediction_1 = tf.nn.dropout(self.prediction_1, self.dropout_keep_prob)

		# put another nn layer to add some non linearity
		self.weight_2 = tf.Variable(tf.truncated_normal([nn_size, nb_class]))
		self.bias_2 = tf.Variable(tf.constant(0.1, shape=[nb_class]))
		self.prediction = tf.nn.softmax(tf.matmul(self.prediction_1, self.weight_2) + self.bias_2)


		self.cross_entropy = -tf.reduce_mean(self.label * tf.log(tf.clip_by_value(self.prediction, 1e-10, 5.0)))
		self.optimizer = tf.train.AdamOptimizer()
		self.minimize = self.optimizer.minimize(self.cross_entropy)


		# performance measure
		self.mistakes = tf.not_equal(tf.argmax(self.label, 1), tf.argmax(self.prediction, 1))
		self.error = tf.reduce_mean(tf.cast(self.mistakes, tf.float32))

		self.correct_prediction = tf.equal(tf.argmax(self.label, 1), tf.argmax(self.prediction, 1))
		self.accuracy = tf.reduce_mean(tf.cast(self.correct_prediction, tf.float32))


		self.bestValidationScore = 0.0

	def testModel(self, xTest, yTest, seqLenTest):

		accuracy = []
		no_of_batches = int(len(xTest)/batch_size)
		ptr = 0
		for i in range(no_of_batches):
			inp, out, seq = xTest[ptr:ptr+batch_size], yTest[ptr:ptr+batch_size], seqLenTest[ptr:ptr+batch_size]
			ptr+=batch_size

			if len(seq) == batch_size:
				acc = self.session.run(self.accuracy, {self.data: inp, self.label: out, self.seqlen:seq, self.dropout_keep_prob:1.0,  self.batch_size:len(out)})
				accuracy.append(acc)


		return sum(accuracy)/float(len(accuracy))

	def giveScores(self, xTest, yTest, seqLenTest):

		all_scores = []


		#if len(seq) == batch_size:
		try:
			scores = self.session.run(self.prediction, {self.data: xTest, self.label: yTest, self.seqlen:seqLenTest, self.dropout_keep_prob:1.0, self.batch_size:len(yTest)})
			for score in scores:
				all_scores.append(score)

			return all_scores
		except:
			return None

	def train(self, xTrain, yTrain, xTest, yTest, seqLenTrain, seqLenTest):

		# initialize variables
		self.session.run(tf.global_variables_initializer())
		saver = tf.train.Saver()

		no_of_batches = int(len(xTrain)/batch_size)

		for i in range(epoch):
			ptr = 0
			accuracy = []
			for j in range(no_of_batches):
				inp, out, seq = xTrain[ptr:ptr+batch_size], yTrain[ptr:ptr+batch_size], seqLenTrain[ptr:ptr+batch_size]
				ptr+=batch_size


				acc = self.session.run([self.accuracy, self.minimize], {self.data: inp, self.label: out, self.seqlen:seq, self.dropout_keep_prob:0.5, self.batch_size:len(out)})
				accuracy.append(acc[0])

			self.accuracy_training.append(sum(accuracy) / float(len(accuracy)))
			print('Epoch {:2d} accuracy on training set {:3.1f}%'.format(i + 1, 100 * self.accuracy_training[-1]))


			# test model on validation set
			if epoch % 1 == 0:
				accuracy = self.testModel(xTest, yTest, seqLenTest)
				self.accuracy_testing.append(accuracy)

				print('Epoch {:2d} accuracy on validation set {:3.1f}%'.format(i + 1, 100 * accuracy))
				if accuracy > self.bestValidationScore:
					print("saving model in disk")
					self.bestValidationScore = accuracy

					# Save all variables of the TensorFlow graph to file.
					save_path = os.path.join(self.save_dir, 'best_validation')
					saver.save(sess=self.session, save_path=save_path)


		self.session.close()

	def restore(self):

		saver = tf.train.Saver()
		save_path = os.path.join(self.save_dir, 'best_validation')
		saver.restore(sess=self.session, save_path=save_path)

	def predict(self, x, seqlen, restore = True):

		if restore:
			self.restore()

		y = [0] * nb_class
		y = [y]
		d_score = self.session.run(self.prediction, {self.data: x, self.label: y, self.seqlen:[seqlen], self.dropout_keep_prob:1.0, self.batch_size:1.0})

		return d_score
