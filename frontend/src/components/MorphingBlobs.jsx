import { motion } from 'framer-motion'

const MorphingBlobs = () => {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden" style={{ zIndex: 0 }}>
      {/* Blob 1 */}
      <motion.div
        className="absolute w-96 h-96 morphing-blob bg-gradient-to-r from-purple-600/20 to-pink-600/20 blur-3xl"
        style={{ top: '10%', left: '10%' }}
        animate={{
          x: [0, 100, 0],
          y: [0, 50, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />

      {/* Blob 2 */}
      <motion.div
        className="absolute w-96 h-96 morphing-blob bg-gradient-to-r from-blue-600/20 to-cyan-600/20 blur-3xl"
        style={{ bottom: '10%', right: '10%' }}
        animate={{
          x: [0, -100, 0],
          y: [0, -50, 0],
          scale: [1, 1.3, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 2,
        }}
      />

      {/* Blob 3 */}
      <motion.div
        className="absolute w-80 h-80 morphing-blob bg-gradient-to-r from-yellow-600/20 to-orange-600/20 blur-3xl"
        style={{ top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}
        animate={{
          scale: [1, 1.5, 1],
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 30,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />

      {/* Blob 4 */}
      <motion.div
        className="absolute w-72 h-72 morphing-blob bg-gradient-to-r from-purple-600/15 to-blue-600/15 blur-3xl"
        style={{ top: '20%', right: '20%' }}
        animate={{
          x: [0, 80, 0],
          y: [0, -80, 0],
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 4,
        }}
      />
    </div>
  )
}

export default MorphingBlobs

