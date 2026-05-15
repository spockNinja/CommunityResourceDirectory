# CommunityResourceDirectory
Enable Communities to List their resources in one place

## Branding Configuration

Once your application is running, you can customize the branding through the Django admin panel at `/admin/constance/config/`:

### Basic Settings
- **COMMUNITY_NAME**: The name of your community (displays in header, hero, and footer)
- **PRIMARY_COLOR**: Primary brand color in hex format (e.g., `#0d6efd`)
- **SECONDARY_COLOR**: Secondary brand color in hex format (e.g., `#6c757d`)

### Image Uploads
- **BANNER_IMAGE**: Upload a hero/banner image (leave empty to use gradient background)
- **FAVICON**: Upload a favicon icon (leave empty for no favicon)

### Image Recommendations

- **Banner Image**: 1920×800px or larger, landscape orientation. Should have good contrast for white text overlay.
- **Favicon**: 32×32px or 16×16px, `.ico`, `.png`, or `.svg` format.

Images are uploaded through the admin interface and stored in the `/media/` directory.
