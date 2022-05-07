class WebpFile < Jekyll::StaticFile
  def destination(dest)
    Pathname.new(super(dest)).sub_ext(".webp")
  end

  def copy_file(dest_path)
    quality = 75

    if !system(
        "/usr/bin/cwebp",
        "-quiet",
        "-mt",
        "-q", quality.to_s,
        path.to_s,
        "-o", dest_path.to_s,
    )
      Jekyll.logger.error "WebP:", "Conversion for input #{path} failed with error #{$?}"
    end

    # From original function
    File.utime(self.class.mtimes[path], self.class.mtimes[path], dest_path)
  end

  def to_webpfile
    nil
  end
end

# Extend the class to allow easy conversions
class ::Jekyll::StaticFile
  def to_webpfile
    return nil unless [".png", ".jpg"].include? extname

    Jekyll.logger.info "WebP:", "Optimising #{@name}"
    WebpFile.new(@site, @base, @dir, @name, @collection)
  end
end

class WebpGen < Jekyll::Generator
  def generate(site)
    site.static_files.each do |file|
      webp = file.to_webpfile
      site.static_files << webp unless webp.nil?
    end
  end
end
