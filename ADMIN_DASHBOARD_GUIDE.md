# 🔧 Admin Dashboard Guide - Garage Focus

## 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Car Management](#car-management)
4. [Asset Upload System](#asset-upload-system)
5. [Supported File Formats](#supported-file-formats)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### Admin Login
1. **Access URL**: `/admin/login`
2. **Default Credentials**:
   - Username: `admin`
   - Password: `garage123`
3. **Changing Credentials**: Update `.env` file:
   ```bash
   ADMIN_USERNAME=your_username
   ADMIN_PASSWORD=your_secure_password
   ```

### First Time Setup
1. Login to admin dashboard
2. Create your first car template
3. Upload assets for each restoration stage
4. Test with a regular user account

---

## 📊 Dashboard Overview

### Main Statistics
- **Total Users**: Number of registered users
- **Car Templates**: Available car models
- **Cars in Progress**: Currently being restored
- **Completed Cars**: Finished restorations
- **Total Focus Hours**: Combined user focus time
- **Success Rate**: Completion percentage

### Quick Actions
- **Add New Car**: Create car templates
- **Upload Assets**: Manage 2D/3D files
- **Manage Cars**: Edit existing templates
- **View App**: Switch to user view

### Recent Activity
- **Recent Users**: Latest registrations
- **Recent Car Activity**: Latest car selections and completions

---

## 🚗 Car Management

### Creating a New Car Template

#### Step 1: Basic Information
- **Model ID**: Unique identifier (lowercase, numbers, underscores)
  - ✅ Good: `mustang_1969`, `ferrari_f40`, `tesla_model_s`
  - ❌ Bad: `Mustang 1969`, `car-1`, `my car!`
- **Display Name**: User-friendly name
  - Examples: "The Stallion", "Classic Beauty", "Electric Beast"
- **Focus Time Required**: Total minutes for 100% restoration
  - **Recommended**: 300 minutes (5 hours)
  - **Range**: 60-1200 minutes (1-20 hours)

#### Step 2: Restoration Stages
Each car automatically gets 5 stages:
1. **0% - Rusted Junk**: Starting condition
2. **25% - Getting Started**: Basic repairs
3. **50% - Half Restored**: Major progress
4. **75% - Almost Done**: Near completion
5. **100% - Showroom Ready**: Perfect condition

### Editing Existing Cars
1. Go to **Manage Cars**
2. Click **Edit** on desired car
3. View asset status for each stage
4. Upload missing assets or remove existing ones

### Deleting Cars
⚠️ **WARNING**: Deletion is permanent!
- Will affect users currently restoring this car
- Consider deactivating instead of deleting

---

## 📁 Asset Upload System

### Upload Process
1. Navigate to **Upload Assets**
2. Select file (drag & drop supported)
3. Choose asset type (2D or 3D)
4. Assign to specific car and stage (optional)
5. Click **Upload Asset**

### Asset Assignment
- **Direct Assignment**: Upload and assign to car/stage immediately
- **Library Upload**: Upload to library, assign later
- **Bulk Upload**: Multiple files for different stages

### File Management
- **Preview**: View 2D images directly
- **Download**: Access 3D models
- **Remove**: Delete assets (permanent)
- **Replace**: Upload new version

---

## 📄 Supported File Formats

### 2D Images
#### Recommended Formats
- **PNG** (best for transparency and quality)
- **JPG/JPEG** (good for photos)
- **GIF** (for simple graphics)

#### Specifications
- **Max File Size**: 16MB
- **Recommended Dimensions**: 512x512px to 1024x1024px
- **Aspect Ratio**: Square (1:1) preferred
- **Color Space**: sRGB

#### Best Practices
- Use high resolution for quality
- Optimize file size for web
- Consider mobile users (smaller screens)

### 3D Models
#### Recommended Formats
1. **GLB** (preferred) - Binary GLTF
   - ✅ Compact file size
   - ✅ Includes textures
   - ✅ Fast loading
   - ✅ Wide browser support

2. **GLTF** - JSON format
   - ✅ Human readable
   - ✅ Good for editing
   - ⚠️ Multiple files

#### Supported Formats
- **FBX** - Autodesk format
- **OBJ** - Wavefront format (basic support)

#### Specifications
- **Max File Size**: 16MB
- **Polygon Count**: 1K-10K triangles (mobile friendly)
- **Textures**: Embedded or external
- **Animation**: Supported (GLB/GLTF)

#### 3D Model Guidelines
- **Low Poly**: Keep polygon count reasonable
- **Textures**: Use PBR materials when possible
- **Scale**: Models auto-scaled to fit viewer
- **Orientation**: Face forward (positive Z-axis)

---

## ✨ Best Practices

### Car Progression Design
1. **Visual Contrast**: Make stages clearly different
2. **Logical Progression**: Rust → Primer → Paint → Polish
3. **Color Schemes**: 
   - 0%: Brown/rust colors
   - 25%: Gray primer
   - 50%: Base color
   - 75%: Rich color
   - 100%: Glossy/metallic finish

### Asset Optimization
- **2D Images**: Use WebP when possible
- **3D Models**: Optimize geometry and textures
- **File Naming**: Use descriptive names
- **Consistency**: Maintain similar quality across stages

### User Experience
- **Loading Speed**: Optimize file sizes
- **Mobile Performance**: Test on mobile devices
- **Fallback Strategy**: Always provide 2D alternatives
- **Progress Feedback**: Clear visual differences

### Content Strategy
- **Car Variety**: Mix classic and modern cars
- **Difficulty Levels**: Different focus time requirements
- **Theme Consistency**: Maintain garage/automotive theme

---

## 🛠️ Troubleshooting

### Common Issues

#### "File Upload Failed"
**Causes:**
- File too large (>16MB)
- Unsupported format
- Server storage full

**Solutions:**
- Compress images/models
- Convert to supported format
- Check server disk space

#### "3D Model Not Loading"
**Causes:**
- Corrupted file
- Invalid geometry
- Missing textures

**Solutions:**
- Re-export from 3D software
- Validate model integrity
- Check texture paths

#### "Asset Not Displaying"
**Causes:**
- Wrong file path
- Database sync issue
- Browser cache

**Solutions:**
- Refresh browser cache
- Restart application
- Check file permissions

### File Format Conversions

#### Converting to GLB (Recommended)
```bash
# Using Blender (free)
1. Import your model (FBX, OBJ, etc.)
2. File > Export > glTF 2.0
3. Choose "Binary" format (.glb)
4. Export

# Using online converters
- https://products.aspose.app/3d/conversion
- https://www.facebook.com/Facebook3D/
```

#### Image Optimization
```bash
# Using ImageMagick
convert input.png -resize 512x512 -quality 85 output.png

# Using online tools
- https://tinypng.com/
- https://squoosh.app/
```

### Performance Tips
- **Monitor Usage**: Check dashboard statistics
- **Clean Up**: Remove unused assets
- **Test Regularly**: Try user experience
- **Backup Data**: Export important assets

### Database Management
```bash
# View uploaded assets
mongosh
use garage_focus
db.car_templates.find().pretty()

# Clean up unused files
# (manually check static/assets/uploads/)
```

---

## 📈 Advanced Features

### Bulk Operations
- Upload multiple assets at once
- Batch assign to different stages
- Export/import car templates

### Custom Themes
- Modify color schemes
- Upload custom textures
- Create themed car collections

### Analytics
- Track user engagement
- Monitor completion rates
- Analyze popular cars

---

## 🔐 Security Considerations

### File Upload Security
- Validate file types server-side
- Scan for malicious content
- Limit file sizes
- Regular cleanup of uploads

### Admin Access
- Use strong passwords
- Change default credentials
- Regular security updates
- Monitor admin activity

### User Data
- Respect user privacy
- Secure data storage
- Regular backups
- GDPR compliance if needed

---

## 📞 Support & Resources

### Getting Help
- Check console logs for errors
- Review server logs
- Test in different browsers
- Document reproduction steps

### Useful Tools
- **3D Software**: Blender (free), Maya, 3ds Max
- **Image Editors**: GIMP (free), Photoshop
- **Conversion Tools**: Online converters, command-line tools
- **Testing**: Multiple devices and browsers

### Documentation
- [Three.js Documentation](https://threejs.org/docs/)
- [GLTF Specification](https://github.com/KhronosGroup/glTF)
- [WebGL Support](https://caniuse.com/webgl)

---

## 🎯 Quick Reference

### Admin URLs
- `/admin/login` - Admin login
- `/admin` - Dashboard home
- `/admin/cars` - Manage car templates
- `/admin/cars/new` - Create new car
- `/admin/upload` - Upload assets
- `/admin/logout` - Logout

### API Endpoints
- `GET /api/car_3d/<model_id>` - Get 3D model data
- `POST /api/admin/update_car_stage` - Update car assets

### File Paths
- `static/assets/uploads/2d/` - 2D image assets
- `static/assets/uploads/3d/` - 3D model assets

### Default Configuration
- Max file size: 16MB
- Supported 2D: PNG, JPG, GIF
- Supported 3D: GLB, GLTF, FBX, OBJ
- Admin username: `admin`
- Admin password: `garage123`

---

**Remember**: The admin dashboard is the control center for your Garage Focus experience. Take time to understand each feature and maintain your assets regularly for the best user experience! 🏁
