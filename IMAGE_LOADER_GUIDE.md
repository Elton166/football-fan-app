# Modern Football Image Loader - Usage Guide

## Overview

The Football Fan App now includes a modern image loading system with:
- ✨ Shimmer loading placeholders
- 🔄 Automatic fallback images
- 🚀 Lazy loading for performance
- 🎨 Smooth animations and hover effects
- ⚽ Football-themed styling

## Features

### 1. **Shimmer Loading Effect**
Images show an animated shimmer placeholder while loading

### 2. **Fallback Images**
If an image fails to load, it automatically shows a fallback

### 3. **Lazy Loading**
Images only load when they're about to enter the viewport

### 4. **Hover Effects**
- Scale and rotate on hover
- Glowing drop shadow
- Smooth transitions

### 5. **Responsive**
Works perfectly on mobile, tablet, and desktop

## How to Use

### Method 1: Automatic Enhancement (Easiest)

Add `data-football-img` attribute to any image:

```html
<img 
    data-football-img
    src="https://crests.football-data.org/PL.png" 
    alt="Premier League"
    data-fallback="/static/images/placeholder.png"
>
```

The JavaScript will automatically:
- Wrap it in a container
- Add shimmer placeholder
- Handle loading states
- Apply fallback on error

### Method 2: Using Template Macros

Import the macros in your template:

```jinja2
{% import "macros.html" as macros %}
```

Then use the helper functions:

#### Football Image (General)
```jinja2
{{ macros.football_image(
    src='https://example.com/image.jpg',
    alt='Match Photo',
    fallback='/static/images/placeholder.png',
    css_class='custom-class',
    width='400',
    height='300'
) }}
```

#### Team Crest
```jinja2
{{ macros.team_crest(
    src=team.crest,
    team_name=team.name,
    size='medium'  # Options: 'small', 'medium', 'large'
) }}
```

#### League Logo
```jinja2
{{ macros.league_logo(
    src=league.emblem,
    league_name=league.name,
    size='80'  # Size in pixels
) }}
```

### Method 3: Manual HTML Structure

```html
<div class="image-container">
    <div class="shimmer-placeholder"></div>
    <img 
        data-football-img
        src="image-url.jpg" 
        alt="Description"
        data-fallback="fallback-url.jpg"
        class="football-image hidden"
        loading="lazy"
    >
</div>
```

## CSS Classes

### Image Container
```css
.image-container
```
- Wraps the image and shimmer
- Provides rounded corners (24px 8px 24px 8px)

### Football Image
```css
.football-image
```
- Main image class
- Handles transitions and hover effects

### Shimmer Placeholder
```css
.shimmer-placeholder
```
- Animated loading placeholder
- Shows while image loads

## Hover Effects

All images with `data-football-img` get these hover effects:
- **Scale**: 1.02x zoom
- **Rotate**: 0.5 degree tilt
- **Glow**: Green drop shadow (#00ff99)
- **Brightness**: 5% increase

## Examples in Your App

### League Logos
```html
<img 
    data-football-img
    src="https://crests.football-data.org/PL.png" 
    alt="Premier League"
    class="league-logo"
>
```

### Team Crests
```html
<img 
    data-football-img
    src="{{ team.crest }}" 
    alt="{{ team.name }}"
    data-fallback="https://via.placeholder.com/50x50/00a86b/ffffff?text={{ team.name[0] }}"
    class="team-crest"
>
```

### Match Highlights
```html
<div class="highlight-thumbnail">
    <img 
        data-football-img
        src="{{ highlight.thumbnail_url }}" 
        alt="{{ highlight.title }}"
        data-fallback="/static/images/highlight-placeholder.png"
    >
</div>
```

## Customization

### Change Shimmer Colors
Edit in `static/css/style.css`:

```css
.shimmer-placeholder {
    background: linear-gradient(
        90deg,
        #your-color-1 0%,
        #your-color-2 20%,
        #your-color-1 40%,
        #your-color-1 100%
    );
}
```

### Change Hover Glow Color
```css
.football-image:hover {
    filter: drop-shadow(0 0 8px #your-color) brightness(1.05);
}
```

### Adjust Border Radius
```css
.image-container,
.football-image,
.shimmer-placeholder {
    border-radius: 24px 8px 24px 8px; /* Customize this */
}
```

## Performance Tips

1. **Use appropriate image sizes** - Don't load 4K images for thumbnails
2. **Lazy loading is automatic** - Images load only when needed
3. **Fallbacks are cached** - Failed images won't retry unnecessarily
4. **Shimmer is CSS-only** - No JavaScript overhead

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers

### Fallback for Older Browsers
- IntersectionObserver not supported? Images load immediately
- CSS animations not supported? Shows static placeholder

## Accessibility

- **Reduced Motion**: Respects `prefers-reduced-motion` setting
- **Alt Text**: Always include descriptive alt text
- **Keyboard Navigation**: All hover effects work with focus states

## Troubleshooting

### Images not loading?
- Check the `src` URL is correct
- Verify CORS settings for external images
- Check browser console for errors

### Shimmer not showing?
- Ensure `image-loader.js` is loaded
- Check that `data-football-img` attribute is present

### Hover effects not working?
- Verify CSS file is loaded
- Check for conflicting CSS rules
- Ensure JavaScript initialized properly

## Examples from Your App

The image loader is already active on:
- ✅ League logos on homepage
- ✅ Team crests in standings
- ✅ Match cards
- ✅ World Cup emblems
- ✅ Fantasy league logos
- ✅ Highlight thumbnails

Just add `data-football-img` to any new images!

---

**Your images now load beautifully with modern effects!** ✨⚽
