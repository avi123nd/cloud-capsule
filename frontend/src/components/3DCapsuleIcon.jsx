import { motion } from 'framer-motion'

const CapsuleIcon3D = ({ size = 80, className = '' }) => {
  return (
    <motion.div
      className={`relative ${className}`}
      style={{
        width: size,
        height: size,
        transformStyle: 'preserve-3d',
      }}
      animate={{
        rotateY: [0, 360],
      }}
      transition={{
        duration: 20,
        repeat: Infinity,
        ease: 'linear',
      }}
    >
      {/* Capsule body */}
      <motion.div
        className="absolute inset-0 rounded-full capsule-glow"
        style={{
          background: 'linear-gradient(135deg, #d4af37 0%, #f4d03f 50%, #d4af37 100%)',
          boxShadow: `
            0 0 20px rgba(212, 175, 55, 0.5),
            0 0 40px rgba(212, 175, 55, 0.3),
            inset 0 0 20px rgba(255, 255, 255, 0.2)
          `,
        }}
        whileHover={{
          scale: 1.1,
          boxShadow: `
            0 0 30px rgba(212, 175, 55, 0.8),
            0 0 60px rgba(212, 175, 55, 0.5),
            inset 0 0 30px rgba(255, 255, 255, 0.3)
          `,
        }}
      >
        {/* Highlight */}
        <div
          className="absolute top-2 left-4 w-8 h-8 rounded-full bg-white/40 blur-sm"
        />
        
        {/* Clock face */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="relative w-12 h-12">
            {/* Clock hands */}
            <motion.div
              className="absolute top-1/2 left-1/2 w-0.5 h-4 bg-slate-900 origin-top"
              style={{ transform: 'translate(-50%, -100%)' }}
              animate={{ rotate: 360 }}
              transition={{ duration: 12, repeat: Infinity, ease: 'linear' }}
            />
            <motion.div
              className="absolute top-1/2 left-1/2 w-0.5 h-6 bg-slate-900 origin-top"
              style={{ transform: 'translate(-50%, -100%)' }}
              animate={{ rotate: 360 }}
              transition={{ duration: 60, repeat: Infinity, ease: 'linear' }}
            />
            {/* Center dot */}
            <div className="absolute top-1/2 left-1/2 w-2 h-2 bg-slate-900 rounded-full transform -translate-x-1/2 -translate-y-1/2" />
          </div>
        </div>

        {/* Shine effect */}
        <motion.div
          className="absolute inset-0 rounded-full overflow-hidden"
          animate={{
            background: [
              'linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.3) 50%, transparent 70%)',
              'linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.5) 50%, transparent 70%)',
              'linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.3) 50%, transparent 70%)',
            ],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      </motion.div>

      {/* Orbiting particles */}
      {[...Array(3)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 bg-capsule-gold rounded-full"
          style={{
            left: '50%',
            top: '50%',
            transformOrigin: `${size / 2}px ${size / 2}px`,
          }}
          animate={{
            rotate: 360,
            x: Math.cos((i * 2 * Math.PI) / 3) * (size / 2 + 15),
            y: Math.sin((i * 2 * Math.PI) / 3) * (size / 2 + 15),
            scale: [1, 1.5, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            rotate: {
              duration: 3 + i,
              repeat: Infinity,
              ease: 'linear',
            },
            scale: {
              duration: 2,
              repeat: Infinity,
              delay: i * 0.5,
            },
            opacity: {
              duration: 2,
              repeat: Infinity,
              delay: i * 0.5,
            },
          }}
        />
      ))}
    </motion.div>
  )
}

export default CapsuleIcon3D

