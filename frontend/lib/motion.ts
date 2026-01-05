import { Variants } from 'framer-motion'

/**
 * Nanobanana Pro Motion System
 * Standardized easing curves and variants for fluid, organic motion.
 */

// Premium easing curves
export const EASE = {
    // Standard exponential ease out for smooth UI transitions
    standard: [0.16, 1, 0.3, 1],
    // Bouncy spring-like feel for playful elements
    spring: { type: 'spring', stiffness: 300, damping: 30 },
    // Smooth gentle ease for backgrounds/fades
    gentle: [0.4, 0, 0.2, 1],
}

// Fade In (Simple)
export const fadeIn: Variants = {
    initial: { opacity: 0 },
    animate: {
        opacity: 1,
        transition: { duration: 0.4, ease: EASE.standard }
    },
    exit: {
        opacity: 0,
        transition: { duration: 0.2, ease: EASE.standard }
    }
}

// Slide Up (Content entry)
export const slideUp: Variants = {
    initial: { opacity: 0, y: 20 },
    animate: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.5, ease: EASE.standard }
    },
    exit: {
        opacity: 0,
        y: 10,
        transition: { duration: 0.3, ease: EASE.standard }
    }
}

// Scale In (Modals/Popovers)
export const scaleIn: Variants = {
    initial: { opacity: 0, scale: 0.95 },
    animate: {
        opacity: 1,
        scale: 1,
        transition: { duration: 0.4, ease: EASE.spring }
    },
    exit: {
        opacity: 0,
        scale: 0.95,
        transition: { duration: 0.2, ease: EASE.standard }
    }
}

// Stagger Container (Lists)
export const staggerContainer = (staggerChildren = 0.1, delayChildren = 0): Variants => ({
    initial: {},
    animate: {
        transition: {
            staggerChildren,
            delayChildren,
        }
    },
    exit: {}
})

// List Item (Child of Stagger)
export const staggerItem: Variants = {
    initial: { opacity: 0, y: 20 },
    animate: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.4, ease: EASE.standard }
    },
    exit: {
        opacity: 0,
        y: -10,
        transition: { duration: 0.2 }
    }
}

// Hover Effect (Cards/Buttons)
export const hoverScale: Variants = {
    initial: { scale: 1 },
    hover: {
        scale: 1.02,
        transition: { duration: 0.2, ease: EASE.standard }
    },
    tap: {
        scale: 0.98,
        transition: { duration: 0.1 }
    }
}
