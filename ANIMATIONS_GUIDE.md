# Article Animations with Anime.js

## Summary

Successfully added Anime.js animation library to your Jekyll blog with comprehensive animations for article pages.

## What Was Added

### 1. **Anime.js Library** (`_includes/anime.html`)
   - Loads the Anime.js CDN (v3.2.1)
   - Included in `default.html` layout (available site-wide)

### 2. **Article Animations** (`_includes/article-animations.html`)
   - Comprehensive animation script for article pages
   - Included in `post.html` layout (article pages only)

## Animation Features

### Page Load Animations
- **Article Header**: Fades in and slides up
- **Article Title**: Delayed fade-in with slide up
- **Tags**: Staggered elastic scale animation

### Scroll-Triggered Animations
All content elements animate as they come into view:

- **Headings (H2-H6)**: Slide in from left
- **Paragraphs**: Fade in and slide up
- **Images**: Fade in with subtle scale
- **Lists**: Staggered slide-in for each item
- **Tables**: Fade in and slide up
- **Blockquotes**: Slide in from left
- **Code Blocks**: Fade in with subtle scale

### Interactive Animations
- **Navigation Links**: Subtle slide on hover

## Technical Details

- **Intersection Observer API**: Used for efficient scroll-triggered animations
- **Performance**: Elements only animate once when they first come into view
- **Smooth Easing**: Uses cubic and elastic easing for natural motion
- **Staggered Effects**: Lists and tags animate with delays for visual interest

## Customization

To adjust animations, edit `_includes/article-animations.html`:

- **Duration**: Change `duration` values (in milliseconds)
- **Delay**: Adjust `delay` values
- **Easing**: Modify `easing` functions (see [Anime.js easing](https://animejs.com/documentation/#pennerFunctions))
- **Distance**: Change `translateX` and `translateY` values

## Example Easing Functions

- `easeOutCubic`: Smooth deceleration
- `easeOutElastic(1, .8)`: Bouncy effect
- `easeInOutQuad`: Smooth acceleration and deceleration

## Browser Support

Anime.js supports all modern browsers:
- Chrome, Firefox, Safari, Edge
- IE 10+ (with polyfills)

## Performance

- Animations use CSS transforms (GPU-accelerated)
- Intersection Observer prevents unnecessary animations
- Elements animate only once per page load
