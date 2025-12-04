# 🚀 Deploying FARM-TAK-AI to Vercel

## Quick Deploy Guide

### Prerequisites
- Vercel account (free at [vercel.com](https://vercel.com))
- GROQ API key from [console.groq.com](https://console.groq.com/)
- Git repository (optional but recommended)

---

## Option 1: Deploy via Vercel CLI (Recommended)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Deploy
```bash
cd "c:\Users\shrey\VERSEL FARMTAK AI\FARM-TAK-AI-"
vercel --prod
```

### Step 4: Set Environment Variables
After deployment, go to your Vercel dashboard:
1. Click on your project
2. Go to **Settings** → **Environment Variables**
3. Add: `GROQ_API_KEY` = `your_actual_groq_api_key`
4. Click **Save**
5. **Redeploy** the project for changes to take effect

---

## Option 2: Deploy via GitHub (Easier)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### Step 2: Import to Vercel
1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **Import Git Repository**
3. Select your `FARM-TAK-AI-` repository
4. Click **Import**

### Step 3: Configure
- **Framework Preset**: Other
- **Build Command**: (leave empty)
- **Output Directory**: (leave empty)
- **Install Command**: `pip install -r requirements.txt`

### Step 4: Add Environment Variable
Before deploying, click **Environment Variables**:
- **Name**: `GROQ_API_KEY`
- **Value**: Your actual Groq API key
- Click **Add**

### Step 5: Deploy
Click **Deploy** and wait 2-3 minutes.

---

## Post-Deployment Testing

### Test Your Deployment

1. **Visit Your URL**: `https://your-project.vercel.app`

2. **Test Voice Feature**:
   - Click the green call button (📞)
   - Allow microphone access
   - Speak a farming question in Hindi
   - Verify AI response

3. **Test API Endpoints**:
   ```bash
   # Health check
   curl https://your-project.vercel.app/api/health
   
   # Farming advice
   curl -X POST https://your-project.vercel.app/api/farming-advice \
     -H "Content-Type: application/json" \
     -d '{"query":"गेहूं की खेती कैसे करें"}'
   ```

---

## Important Notes

### ⚠️ Voice Recognition Requirements
- **HTTPS Required**: Voice recognition only works on HTTPS (Vercel provides this)
- **Browser Support**: Chrome, Edge, or Safari
- **Microphone Permission**: Users must allow microphone access

### 🔑 Environment Variables
Make sure to set `GROQ_API_KEY` in Vercel dashboard:
1. Project Settings → Environment Variables
2. Add `GROQ_API_KEY`
3. Redeploy after adding

### 📁 Files Created for Deployment
- ✅ `vercel.json` - Vercel configuration
- ✅ `api/index.py` - Serverless entry point
- ✅ `requirements.txt` - Python dependencies (moved to root)
- ✅ `env.example` - Environment variable template

---

## Troubleshooting

### Issue: "API key की समस्या है"
**Solution**: Environment variable not set
- Go to Vercel Dashboard → Settings → Environment Variables
- Add `GROQ_API_KEY`
- Redeploy the project

### Issue: Voice not working
**Solution**: 
- Ensure you're using HTTPS (Vercel provides this automatically)
- Use Chrome or Edge browser
- Allow microphone permissions

### Issue: Deployment fails
**Solution**:
- Check `requirements.txt` is in root directory
- Verify `vercel.json` syntax
- Check Vercel deployment logs

---

## Custom Domain (Optional)

### Add Your Own Domain
1. Go to Project Settings → Domains
2. Click **Add Domain**
3. Enter your domain name
4. Follow DNS configuration instructions

---

## Monitoring & Logs

### View Deployment Logs
1. Go to Vercel Dashboard
2. Click on your project
3. Go to **Deployments** tab
4. Click on a deployment to view logs

### Monitor Usage
- Go to **Analytics** to see visitor stats
- Check **Functions** tab for serverless function calls

---

## Cost Information

### Vercel Pricing
- **Free Tier**: 
  - ✅ 100GB bandwidth/month
  - ✅ Unlimited deployments
  - ✅ Great for testing and small projects

- **Pro Tier** ($20/month):
  - Unlimited bandwidth
  - Better performance
  - Team features

### GROQ API Pricing
- **Free Tier**: Generous free quota
- Check [groq.com/pricing](https://groq.com/pricing) for limits

---

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Set environment variables
3. ✅ Test the deployment
4. 📱 Share the URL with farmers
5. 📊 Monitor usage and feedback

---

**🌾 Your FARM-TAK-AI is ready to help farmers worldwide! 🚀**
