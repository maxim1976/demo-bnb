# Gancheng B&B - AI Coding Instructions

## Project Overview
This is a **Flask web application** for Gancheng B&B, a bed and breakfast located in Hualien, Taiwan. The frontend uses a single-page template with no build process. The Flask backend provides API endpoints for future contact forms, booking systems, and dynamic data.

## Technology Stack
- **Backend**: Flask 3.0 (Python web framework)
- **Frontend**: Pure HTML templates (Jinja2) with inline JavaScript
- **Tailwind CSS** via CDN (`cdn.tailwindcss.com`) with custom config
- **Google Fonts**: Plus Jakarta Sans (primary font)
- **Material Symbols** icon font for UI icons
- **No frontend build step**: vanilla HTML/CSS served by Flask

## Design System

### Custom Tailwind Configuration
The project extends Tailwind with these custom tokens (defined in `<script id="tailwind-config">`):

```javascript
colors: {
    "primary": "#1152d4",           // Brand blue
    "background-light": "#f6f6f8",  // Light mode background
    "background-dark": "#101622",   // Dark mode background
}
fontFamily: {
    "display": ["Plus Jakarta Sans", "sans-serif"]
}
```

### Dark Mode
- Uses Tailwind's `class` strategy: `<html class="light">` or `<html class="dark">`
- Dark mode variants applied with `dark:` prefix (e.g., `dark:bg-background-dark`)
- Currently hardcoded to light mode - no toggle implemented

### Icon System
- Uses **Material Symbols Outlined** font
- Icons rendered via `<span class="material-symbols-outlined">icon_name</span>`
- Common icons: `menu`, `concierge`, `spa`, `landscape`, `wifi`, `arrow_forward`, `home_pin`

## Layout Structure

### Responsive Patterns
- **Mobile-first approach**: base styles are mobile, desktop uses `md:` and `lg:` prefixes
- **Breakpoint**: `md` is the primary breakpoint for mobile→desktop transitions
- **Container**: `max-w-[1280px] mx-auto` centers content with consistent max width
- **Padding**: Mobile uses `px-4`, desktop uses `md:px-10`

### Section Anatomy
Every major section follows this pattern:
```html
<section class="w-full px-4 md:px-10 py-[spacing]">
    <div class="max-w-[960px] mx-auto">
        <!-- Content -->
    </div>
</section>
```

## Component Patterns

### Hero Images
Background images use inline styles with gradient overlays:
```html
style='background-image: linear-gradient(rgba(0, 0, 0, 0.2) 0%, rgba(0, 0, 0, 0.5) 100%), 
       url("https://lh3.googleusercontent.com/...")'
```

### Cards (Rooms, Features)
- Rounded corners: `rounded-xl` for cards, `rounded-2xl` for sections
- Hover states: `hover:shadow-md`, `group-hover:scale-105`, `group-hover:text-primary`
- Use `group` and `group-hover:` for parent-child interactive states

### Buttons
- **Primary CTA**: `bg-primary text-white shadow-lg shadow-primary/20`
- **Secondary**: `border border-slate-300 text-slate-900`
- Heights: `h-10` (small), `h-12` (large)
- Always include `transition-*` utilities for interactions

## Common Conventions

### Image Accessibility
Every `background-image` div includes `data-alt` attribute describing the image content:
```html
<div ... data-alt="Modern hotel room interior with large window facing mountains">
```

### Spacing Scale
- Section vertical padding: `py-10`, `py-12`, `md:py-20`
- Gap between elements: `gap-4`, `gap-6`, `gap-8`, `gap-12`
- Never arbitrary values outside existing Tailwind scale

### Color Usage
- Text primary: `text-slate-900 dark:text-white`
- Text secondary: `text-slate-600 dark:text-slate-300`
- Text muted: `text-slate-500 dark:text-slate-400`
- Borders: `border-gray-200 dark:border-gray-700`

## Development Workflow

### Running the App
1. Install dependencies: `pip install -r requirements.txt`
2. Run Flask server: `python app.py`
3. Visit `http://localhost:5000`
4. Changes to templates refresh automatically in debug mode

### Making Template Changes
1. Edit `templates/index.html` directly
2. Refresh browser to see changes (Flask auto-reloads templates)
3. Test dark mode by changing `<html class="light">` to `<html class="dark">`
4. No build step required

### Adding Backend Features
- **New routes**: Add to [app.py](app.py) following existing patterns
- **API endpoints**: Use `/api/` prefix, return JSON with `jsonify()`
- **Database**: Install Flask-SQLAlchemy, create models in separate file
- **Forms**: Use Flask-WTF for validation, process in POST routes

### Project Structure
```
gangcheng/
├── app.py                     # Flask app with routes & API endpoints
├── templates/
│   └── index.html            # Homepage template (Jinja2)
├── static/                    # Static assets (currently unused - using CDN)
├── requirements.txt          # Python dependencies
└── code.html                 # Original static version (reference only)
```
