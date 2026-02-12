import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Lock, Clock, Mail, Sparkles } from 'lucide-react'

const Landing = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('token')
    setIsLoggedIn(!!token)
  }, [])

  const features = [
    {
      icon: Lock,
      title: "Secure Encryption",
      description: "Your memories are protected with AES-256 encryption and stored safely in the cloud."
    },
    {
      icon: Clock,
      title: "Time Capsule",
      description: "Set unlock dates and let time preserve your messages until the perfect moment."
    },
    {
      icon: Mail,
      title: "Email Notifications",
      description: "Recipients get notified when their capsule is ready to open."
    }
  ]

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-neutral-100">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-neutral-900 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">T</span>
            </div>
            <span className="text-xl font-semibold text-neutral-900">Time Capsule</span>
          </div>
          <div className="flex items-center space-x-4">
            {isLoggedIn ? (
              <Link
                to="/dashboard"
                className="px-6 py-2 bg-neutral-900 text-white rounded-lg font-medium hover:bg-neutral-800 transition-colors"
              >
                Dashboard
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 text-neutral-600 hover:text-neutral-900 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-6 py-2 bg-neutral-900 text-white rounded-lg font-medium hover:bg-neutral-800 transition-colors"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-neutral-100 rounded-full text-neutral-600 text-sm mb-8">
              <Sparkles className="w-4 h-4" />
              <span>Send messages to the future</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold text-neutral-900 mb-6 leading-tight">
              Time Capsules for<br />
              <span className="text-neutral-400">Meaningful Moments</span>
            </h1>
            
            <p className="text-xl text-neutral-500 mb-12 max-w-2xl mx-auto">
              Create, schedule, and send encrypted time capsules to your loved ones. 
              Lock away memories, messages, and files until the perfect moment arrives.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/register"
                className="inline-flex items-center space-x-2 px-8 py-4 bg-neutral-900 text-white rounded-xl font-medium hover:bg-neutral-800 transition-all hover:scale-105"
              >
                <span>Send a Capsule</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center space-x-2 px-8 py-4 border border-neutral-200 text-neutral-700 rounded-xl font-medium hover:bg-neutral-50 transition-all"
              >
                <span>Sign In</span>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mb-4">
              Why Time Capsule Cloud?
            </h2>
            <p className="text-lg text-neutral-500 max-w-2xl mx-auto">
              Send memories through time with complete security and peace of mind.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="p-8 bg-neutral-50 rounded-2xl hover:bg-neutral-100 transition-colors"
              >
                <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center mb-6 shadow-sm">
                  <feature.icon className="w-6 h-6 text-neutral-700" />
                </div>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-neutral-500 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mb-4">
              How It Works
            </h2>
          </motion.div>

          <div className="space-y-12">
            {[
              { step: "01", title: "Create", desc: "Upload files, write messages, or record videos for your capsule." },
              { step: "02", title: "Schedule", desc: "Set an unlock date in the future - days, months, or years ahead." },
              { step: "03", title: "Send", desc: "Share with friends and family via email." },
              { step: "04", title: "Unlock", desc: "On the unlock date, the capsule opens automatically with email notification." }
            ].map((item, index) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
                className="flex items-start space-x-6"
              >
                <div className="flex-shrink-0 w-16 h-16 bg-neutral-900 rounded-2xl flex items-center justify-center">
                  <span className="text-white font-bold text-xl">{item.step}</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-neutral-900 mb-2">
                    {item.title}
                  </h3>
                  <p className="text-neutral-500">{item.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 bg-neutral-900">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to Send to the Future?
            </h2>
            <p className="text-neutral-400 mb-8 text-lg">
              Start creating meaningful time capsules today.
            </p>
            <Link
              to="/register"
              className="inline-flex items-center space-x-2 px-8 py-4 bg-white text-neutral-900 rounded-xl font-medium hover:bg-neutral-100 transition-all hover:scale-105"
            >
              <span>Get Started Free</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-neutral-200">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-neutral-900 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <span className="text-neutral-600">Time Capsule Cloud</span>
          </div>
          <p className="text-neutral-400 text-sm">
            © 2024 Time Capsule Cloud. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Landing
