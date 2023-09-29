import tensorflow as tf
from tensorflow_probability import distributions as tfd
import numpy as np

def bayesian_inference(predictions):
    data = predictions
    # Define the prior distribution
    prior_mean = tfd.Normal(loc=0, scale=1)
    prior_stddev = tfd.HalfNormal(scale=1)

    # Define the likelihood function
    def likelihood(mu, sigma):
        dist = tfd.Normal(loc=mu, scale=sigma)
        return tf.reduce_prod(dist.prob(data))

    # Define the posterior distribution
    @tf.function
    def posterior(mu, sigma):
        return likelihood(mu, sigma) * prior_mean.prob(mu) * prior_stddev.prob(sigma)

    # Define the optimizer
    optimizer = tf.optimizers.Adam()
    # Optimize the posterior distribution
    mu = tf.Variable(0.0)
    sigma = tf.Variable(1.0)

    for i in range(1000):
        with tf.GradientTape() as tape:
            loss = -tf.math.log(posterior(mu, sigma))
        gradients = tape.gradient(loss, [mu, sigma])
        optimizer.apply_gradients(zip(gradients, [mu, sigma]))

    # Get the posterior distribution
    posterior_mean = mu.numpy()
    posterior_stddev = sigma.numpy()
    return posterior_mean, posterior_stddev