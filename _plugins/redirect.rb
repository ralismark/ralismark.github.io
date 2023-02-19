# Inspired by https://github.com/tsmango/jekyll_alias_generator/blob/master/alias_generator.rb

module Jekyll
  class AliasGenerator < Generator
    def generate(site)
      site.posts.docs.each do |post|
        # posts after this time don't need a backcompat alias
        if post.data["date"] > Time.new(2021, 1, 1)
          next
        end

        alias_path = URL.new(
          :template => "/:year/:month/:day/:title:output_ext",
          :placeholders => post.url_placeholders
        )
        link(site, alias_path, post.url)
      end
    end

    def link(site, source, target)
      alias_path = File.join('/', source.to_s)

      alias_dir = File.extname(alias_path).empty? ? alias_path : File.dirname(alias_path)
      alias_basename = File.extname(alias_path).empty? ? "index.html" : File.basename(alias_path)

      # Make sure jekyll know about them
      alias_file = Jekyll::AliasFile.new(site, site.dest, alias_dir, alias_basename)
      alias_file.set_target(target)
      site.static_files << alias_file
    end
  end

  # File that is aliased
  class AliasFile < StaticFile
    def modified?
      return false
    end

    def set_target(target)
      @target = target
    end

    def write(dest)
      contents = <<-EOF
      <!DOCTYPE html>
      <html>
        <title>Redirecting...</title>
        <meta charset="utf-8">
        <link rel="canonical" href="#{@target}">
        <meta http-equiv="content-type" content="text/html; charset=utf-8">
        <meta http-equiv="refresh" content="0;url=#{@target}">
        <meta name="robots" content="noindex">
        <a href="#{@target}">Click here if you are not redirected</a>
      </html>
      EOF

      dest_path = destination(dest)
      FileUtils.mkdir_p(File.dirname(dest_path))
      File.open(destination(dest), "w") do |file|
        file.write(contents)
      end
      true
    end
  end
end
