import { useEffect, useRef } from 'react'

const AdvancedParticles = ({ count = 100 }) => {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    let animationFrameId
    let particles = []

    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    class Particle {
      constructor() {
        this.reset()
      }

      reset() {
        this.x = Math.random() * canvas.width
        this.y = Math.random() * canvas.height
        this.size = Math.random() * 3 + 1
        this.speedX = (Math.random() - 0.5) * 0.5
        this.speedY = (Math.random() - 0.5) * 0.5
        this.opacity = Math.random() * 0.5 + 0.2
        this.hue = 45 + Math.random() * 30 // Gold tones
        this.pulseSpeed = Math.random() * 0.02 + 0.01
        this.pulsePhase = Math.random() * Math.PI * 2
      }

      update() {
        this.x += this.speedX
        this.y += this.speedY

        // Wrap around edges
        if (this.x < 0) this.x = canvas.width
        if (this.x > canvas.width) this.x = 0
        if (this.y < 0) this.y = canvas.height
        if (this.y > canvas.height) this.y = 0

        // Pulsing
        this.pulsePhase += this.pulseSpeed
        const pulse = Math.sin(this.pulsePhase) * 0.3 + 0.7
        this.currentOpacity = this.opacity * pulse
      }

      draw() {
        ctx.beginPath()
        
        // Create gradient for each particle
        const gradient = ctx.createRadialGradient(
          this.x, this.y, 0,
          this.x, this.y, this.size * 2
        )
        gradient.addColorStop(0, `hsla(${this.hue}, 70%, 60%, ${this.currentOpacity})`)
        gradient.addColorStop(0.5, `hsla(${this.hue}, 70%, 60%, ${this.currentOpacity * 0.5})`)
        gradient.addColorStop(1, `hsla(${this.hue}, 70%, 60%, 0)`)

        ctx.fillStyle = gradient
        ctx.arc(this.x, this.y, this.size * 2, 0, Math.PI * 2)
        ctx.fill()

        // Outer glow
        ctx.shadowBlur = 10
        ctx.shadowColor = `hsla(${this.hue}, 70%, 60%, ${this.currentOpacity})`
        ctx.fill()
        ctx.shadowBlur = 0
      }
    }

    // Create particles
    for (let i = 0; i < count; i++) {
      particles.push(new Particle())
    }

    // Connection lines
    const drawConnections = () => {
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < 150) {
            ctx.beginPath()
            ctx.strokeStyle = `rgba(212, 175, 55, ${0.1 * (1 - distance / 150)})`
            ctx.lineWidth = 0.5
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.stroke()
          }
        }
      }
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Update and draw connections
      drawConnections()

      // Update and draw particles
      particles.forEach((particle) => {
        particle.update()
        particle.draw()
      })

      animationFrameId = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      cancelAnimationFrame(animationFrameId)
    }
  }, [count])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none opacity-40"
      style={{ zIndex: 0 }}
    />
  )
}

export default AdvancedParticles

