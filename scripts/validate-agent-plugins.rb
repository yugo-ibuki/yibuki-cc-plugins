#!/usr/bin/env ruby

require "json"
require "pathname"
require "yaml"

ROOT = Pathname.new(__dir__).parent.freeze
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
PLUGIN_FIELDS = %w[$schema name version description author homepage repository license keywords extensions].freeze
SKILL_FIELDS = %w[name description license compatibility metadata allowed-tools].freeze
PLUGIN_NAME = /\A(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\z/
SKILL_NAME = /\A(?!.*--)[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\z/
SEMVER = /\A\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?\z/

def relative(path)
  path.relative_path_from(ROOT)
end

def validate_manifest(plugin, errors)
  path = plugin.join("plugin.json")
  unless path.file?
    errors << "missing manifest: #{relative(path)}"
    return
  end

  manifest = JSON.parse(path.read)
  unknown = manifest.keys - PLUGIN_FIELDS
  errors << "unknown manifest fields in #{relative(path)}: #{unknown.join(', ')}" unless unknown.empty?
  errors << "wrong schema in #{relative(path)}" unless manifest["$schema"] == PLUGIN_SCHEMA

  name = manifest["name"]
  valid_name = name.is_a?(String) && name.length.between?(1, 64) && PLUGIN_NAME.match?(name)
  errors << "invalid plugin name in #{relative(path)}" unless valid_name
  errors << "plugin name/directory mismatch in #{relative(path)}" unless name == plugin.basename.to_s

  %w[version description homepage repository license].each do |field|
    errors << "#{field} must be a string in #{relative(path)}" if manifest.key?(field) && !manifest[field].is_a?(String)
  end
  if manifest.key?("version") && manifest["version"].is_a?(String) && !SEMVER.match?(manifest["version"])
    errors << "version is not SemVer in #{relative(path)}"
  end

  if manifest.key?("author")
    author = manifest["author"]
    unless author.is_a?(Hash)
      errors << "author must be an object in #{relative(path)}"
    else
      unknown_author = author.keys - %w[name email url]
      errors << "unknown author fields in #{relative(path)}: #{unknown_author.join(', ')}" unless unknown_author.empty?
      author.each do |field, value|
        errors << "author.#{field} must be a string in #{relative(path)}" unless value.is_a?(String)
      end
    end
  end

  if manifest.key?("keywords") && (!manifest["keywords"].is_a?(Array) || !manifest["keywords"].all? { |item| item.is_a?(String) })
    errors << "keywords must be an array of strings in #{relative(path)}"
  end
  if manifest.key?("extensions") && (!manifest["extensions"].is_a?(Hash) || !manifest["extensions"].values.all? { |item| item.is_a?(Hash) })
    errors << "extensions must map namespaces to objects in #{relative(path)}"
  end
rescue JSON::ParserError => e
  errors << "invalid JSON #{relative(path)}: #{e.message}"
end

def validate_skill(skill, errors)
  path = skill.join("SKILL.md")
  unless path.file?
    errors << "missing SKILL.md: #{relative(skill)}"
    return
  end

  content = path.read
  match = content.match(/\A---\s*\n(.*?)\n---\s*\n/m)
  unless match
    errors << "invalid frontmatter boundary: #{relative(path)}"
    return
  end

  metadata = YAML.safe_load(match[1], permitted_classes: [], permitted_symbols: [], aliases: false)
  unless metadata.is_a?(Hash)
    errors << "frontmatter is not an object: #{relative(path)}"
    return
  end

  unknown = metadata.keys.map(&:to_s) - SKILL_FIELDS
  errors << "unknown skill fields in #{relative(path)}: #{unknown.join(', ')}" unless unknown.empty?

  name = metadata["name"]
  valid_name = name.is_a?(String) && name.length.between?(1, 64) && SKILL_NAME.match?(name)
  errors << "invalid skill name in #{relative(path)}" unless valid_name
  errors << "skill name/directory mismatch in #{relative(path)}" unless name == skill.basename.to_s

  description = metadata["description"]
  errors << "invalid skill description in #{relative(path)}" unless description.is_a?(String) && description.length.between?(1, 1024)
  errors << "skill exceeds the recommended 500 lines: #{relative(path)}" if content.lines.count > 500

  %w[license compatibility allowed-tools].each do |field|
    errors << "#{field} must be a string in #{relative(path)}" if metadata.key?(field) && !metadata[field].is_a?(String)
  end
  if metadata.key?("compatibility") && metadata["compatibility"].is_a?(String) && !metadata["compatibility"].length.between?(1, 500)
    errors << "compatibility must be 1-500 characters in #{relative(path)}"
  end
  if metadata.key?("metadata") && (!metadata["metadata"].is_a?(Hash) || !metadata["metadata"].all? { |key, value| key.is_a?(String) && value.is_a?(String) })
    errors << "metadata must map strings to strings in #{relative(path)}"
  end
rescue Psych::SyntaxError => e
  errors << "invalid YAML #{relative(path)}: #{e.message}"
end

def validate_markdown_links(errors)
  ROOT.glob("plugins/**/*.md").sort.each do |markdown|
    fence = nil
    content = markdown.readlines.each_with_object([]) do |line, visible|
      if fence
        fence = nil if line.match?(/^#{Regexp.escape(fence)}#{Regexp.escape(fence[0])}*\s*$/)
      elsif (match = line.match(/^(?<fence>`{3,}|~{3,})/))
        fence = match[:fence]
      else
        visible << line
      end
    end.join
    content.scan(/\[[^\]]*\]\(([^)]+)\)/).flatten.each do |target|
      target = target.split(/\s+/, 2).first
      next if target.nil? || target.empty? || target.start_with?("#") || target.match?(/\A[a-z][a-z0-9+.-]*:/i)

      decoded = target.gsub("%20", " ").split("#", 2).first
      resolved = markdown.dirname.join(decoded).cleanpath
      errors << "broken link #{target} in #{relative(markdown)}" unless resolved.exist?
    end
  end
end

errors = []
plugins = ROOT.glob("plugins/*").select(&:directory?).sort
errors << "no plugins found" if plugins.empty?

skill_count = 0
plugins.each do |plugin|
  validate_manifest(plugin, errors)
  skills = plugin.join("skills")
  unless skills.directory?
    errors << "missing skills directory: #{relative(skills)}"
    next
  end

  skills.children.select(&:directory?).sort.each do |skill|
    validate_skill(skill, errors)
    skill_count += 1 if skill.join("SKILL.md").file?
  end
end

validate_markdown_links(errors)
ROOT.glob("plugins/**/{.claude-plugin,commands}").each do |path|
  errors << "non-portable path remains: #{relative(path)}"
end
errors << "Claude marketplace remains" if ROOT.join(".claude-plugin/marketplace.json").exist?

if errors.empty?
  puts "PASS: #{plugins.length} plugins, #{skill_count} skills, manifests/frontmatter/links valid"
else
  warn errors.join("\n")
  exit 1
end
