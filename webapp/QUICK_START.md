# Quick Start Guide

Get your Jacobi Heat Simulation Web App running in minutes!

## 🚀 Quick Local Test (5 minutes)

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Start the Application

**Option A: Use the start script (macOS/Linux)**
```bash
./start_local.sh
```

**Option B: Manual start**

Terminal 1 - Backend:
```bash
cd backend
python app.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm start
```

### 3. Open Your Browser

Navigate to: `http://localhost:3000`

### 4. Run a Simulation

1. You'll see a beautiful welcome screen
2. Enter hot-square sizes (defaults are 0.1, 0.2, 0.33)
3. Click "🚀 Run Simulations"
4. Watch the magic happen! ✨

## ☁️ Deploy to Render (10 minutes)

### Automated Deployment

1. Push to GitHub:
```bash
git init
git add .
git commit -m "Jacobi simulation webapp"
git remote add origin <your-repo-url>
git push -u origin main
```

2. Deploy on Render:
   - Go to https://dashboard.render.com/
   - Click "New" → "Blueprint"
   - Connect your repository
   - Select the `webapp` directory
   - Click "Apply"
   - ☕ Wait 5-10 minutes for deployment

3. Done! Your app is live! 🎉

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

## 📱 What You'll See

### Welcome Screen
- Clean, modern interface
- Input fields for 3 different hot-square sizes
- Beautiful gradient background
- Smooth animations

### Simulation Dashboard
- **Left Panel**: Three simulations running side-by-side
  - Real-time temperature visualizations
  - Iteration counts and delta values
  - Convergence indicators
  
- **Right Panel**: Live convergence plot
  - Real-time graph comparing all three simulations
  - Logarithmic scale for delta values
  - Color-coded for easy comparison
  - Results summary when complete

## 🎨 Features

- ✅ Real-time WebSocket streaming
- ✅ Beautiful turbo colormap
- ✅ Live convergence plotting
- ✅ Smooth animations with Framer Motion
- ✅ Responsive design
- ✅ Professional gradient UI
- ✅ One-click deployment to Render

## 📊 Research Question

**Does the hot-square size change the difficulty of the solve?**

The app lets you test this by running three simulations simultaneously with different hot-square sizes and comparing their convergence behavior in real-time.

**Expected Result**: Larger hot squares converge faster! 🔥

## 🛠 Tech Stack

**Backend:**
- Flask + Flask-SocketIO
- NumPy + Matplotlib
- Gunicorn + Eventlet

**Frontend:**
- React 18
- Socket.IO Client
- Recharts
- Framer Motion

## 📝 File Structure

```
webapp/
├── backend/
│   ├── app.py                 # Flask server with WebSocket
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html         # HTML template
│   ├── src/
│   │   ├── components/
│   │   │   ├── WelcomeScreen.js    # Landing page
│   │   │   └── SimulationView.js   # Dashboard
│   │   ├── App.js             # Main React app
│   │   ├── App.css            # Styles
│   │   └── index.js           # Entry point
│   └── package.json           # Node dependencies
├── render.yaml                # Deployment config
├── README.md                  # Full documentation
├── DEPLOYMENT_GUIDE.md        # Detailed deployment steps
└── QUICK_START.md            # This file!
```

## 🎯 Next Steps

1. ✅ Get it running locally
2. ✅ Test different hot-square sizes
3. ✅ Deploy to Render
4. ✅ Share your live URL!
5. 📊 Use for your research presentation

## 💡 Tips

- **Development**: Use `npm start` for hot-reload during development
- **Production**: Render handles building and serving automatically
- **Performance**: Free tier may be slower; consider upgrading for demos
- **Customization**: Edit `App.css` to change colors and styles

## 🐛 Common Issues

**Backend won't start:**
```bash
# Make sure you're in the backend directory
cd backend
# Check Python version (needs 3.9+)
python --version
# Reinstall dependencies
pip install -r requirements.txt
```

**Frontend won't start:**
```bash
# Make sure you're in the frontend directory
cd frontend
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**WebSocket won't connect:**
- Check that backend is running on port 5000
- Verify frontend proxy in `package.json`
- Check browser console for errors

## 📞 Need Help?

- Check `README.md` for full documentation
- See `DEPLOYMENT_GUIDE.md` for deployment help
- Review browser console for errors
- Check Render logs in dashboard

---

**Happy Simulating!** 🔥🚀

