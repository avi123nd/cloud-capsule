import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

const SparkleRain = ({ count = 30 }) => {
  const [sparkles, setSparkles] = useState([])

  useEffect(() => {
    const newSparkles = Array.from({ length: count }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      delay: Math.random() * 3,
      duration: 2 + Math.random() * 3,
      size: Math.random() * 4 + 2,
    }))
    setSparkles(newSparkles)
  }, [count])

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden" style={{ zIndex: 1 }}>
      {sparkles.map((sparkle) => (
        <motion.div
          key={sparkle.id}
          className="absolute rounded-full"
          style={{
            left: `${sparkle.x}%`,
            width: sparkle.size,
            height: sparkle.size,
            background: 'radial-gradient(circle, rgba(212, 175, 55, 1) 0%, transparent 70%)',
            boxShadow: '0 0 10px rgba(212, 175, 55, 0.8), 0 0 20px rgba(212, 175, 55, 0.4)',
          }}
          initial={{
            y: -20,
            opacity: 0,
            scale: 0,
          }}
          animate={{
            y: '110vh',
            opacity: [0, 1, 1, 0],
            scale: [0, 1, 1, 0],
            x: [
              sparkle.x,
              sparkle.x + (Math.random() - 0.5) * 20,
              sparkle.x - (Math.random() - 0.5) * 20,
              sparkle.x,
            ],
          }}
          transition={{
            duration: sparkle.duration,
            delay: sparkle.delay,
            repeat: Infinity,
            ease: 'easeIn',
          }}
        />
      ))}
    </div>
  )
}

export default SparkleRain

