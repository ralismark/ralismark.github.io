# Inspired by https://github.com/tsmango/jekyll_alias_generator/blob/master/alias_generator.rb

module Jekyll

  class AliasGenerator < Generator

    def generate(site)
      @site = site

      @site.posts.docs.each do |post|
        if post.data["date"] < Time.new(2023, 1, 1)
          from = URL.new(
            :template => "/:year/:month/:day/:title:output_ext",
            :placeholders => post.url_placeholders
          )
          generate_aliases(post.url, from)
        end
      end
    end

    def generate_aliases(destination_path, aliases)
      # Handle lists of sources
      alias_paths ||= Array.new
      alias_paths << aliases
      alias_paths.compact!

      alias_paths.flatten.each do |alias_path|
        # Generate parts of the path
        alias_path = File.join('/', alias_path.to_s)
        alias_dir  = File.extname(alias_path).empty? ? alias_path : File.dirname(alias_path)
        alias_file = File.extname(alias_path).empty? ? "index.html" : File.basename(alias_path)

        fs_path_to_dir = File.join(@site.dest, alias_dir)
        alias_sections = alias_dir.split('/')[1..-1]

        # Make sure parent directory exists
        FileUtils.mkdir_p(fs_path_to_dir)

        # Create alias path
        File.open(File.join(fs_path_to_dir, alias_file), 'w') do |file|
          file.write(alias_template(destination_path))
        end

        # Make sure jekyll know about them
        @site.static_files << Jekyll::AliasFile.new(@site, @site.dest, alias_dir, alias_file)
      end
    end

    # Generate the redirect document
    def alias_template(destination_path)
      <<-EOF
      <!DOCTYPE html>
      <html>
        <title>Redirecting...</title>
        <meta charset="utf-8">
        <link rel="canonical" href="#{destination_path}">
        <meta http-equiv="content-type" content="text/html; charset=utf-8">
        <meta http-equiv="refresh" content="0;url=#{destination_path}">
        <meta name="robots" content="noindex">
        <a href="#{destination_path}">Click here if you are not redirected</a>
      </html>
      EOF
    end
  end

  # File that is aliased
  class AliasFile < StaticFile
    require 'set'

    def modified?
      return false
    end

    def write(dest)
      return true
    end
  end
end
