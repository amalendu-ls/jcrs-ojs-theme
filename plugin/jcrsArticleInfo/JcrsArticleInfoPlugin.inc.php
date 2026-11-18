<?php

/**
 * @file plugins/generic/jcrsArticleInfo/JcrsArticleInfoPlugin.inc.php
 *
 * Journal of Cultural Research Studies (JCRS)
 *
 * Adds, under every article in an issue's table of contents (home page and issue pages):
 *  - abstract view and download counts (from OJS usage statistics, all time)
 *  - an expandable abstract with keywords
 *
 * Uses the Templates::Issue::Issue::Article hook that the Default theme's
 * article_summary.tpl already calls, so no theme templates are overridden.
 * Styling comes from the journal style sheet (jcrs-custom.css).
 */

import('lib.pkp.classes.plugins.GenericPlugin');

class JcrsArticleInfoPlugin extends GenericPlugin {

	/** @var array submissionId => [views, downloads] */
	private $countsCache = [];

	public function register($category, $path, $mainContextId = null) {
		$success = parent::register($category, $path, $mainContextId);
		if ($success && $this->getEnabled($mainContextId)) {
			HookRegistry::register('Templates::Issue::Issue::Article', [$this, 'addArticleInfo']);
		}
		return $success;
	}

	public function getDisplayName() {
		return 'JCRS Article Information';
	}

	public function getDescription() {
		return 'Shows abstract view and download counts and an expandable abstract for each article in issue tables of contents.';
	}

	/**
	 * Append the counts and abstract toggle to the article summary.
	 */
	public function addArticleInfo($hookName, $args) {
		$smarty = $args[1];
		$output =& $args[2];
		try {
			$article = $smarty->getTemplateVars('article');
			if (!$article) {
				return false;
			}
			$publication = $article->getCurrentPublication();
			$abstract = $publication ? (string) $publication->getLocalizedData('abstract') : '';
			$keywords = $publication ? (array) $publication->getLocalizedData('keywords') : [];
			$title = $publication ? (string) $publication->getLocalizedData('title') : '';
			$lang = preg_match('/\p{Bengali}/u', $title . $abstract) ? ' lang="bn"' : '';

			$html = '';
			try {
				list($views, $downloads) = $this->getCounts((int) $article->getId());
				$html .= '<div class="jcrs-art-stats">'
					. '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 14V9h2.5v5H2Zm4.75 0V5h2.5v9h-2.5ZM11.5 14V2H14v12h-2.5Z"/></svg>'
					. 'Abstract views: ' . (int) $views
					. '<span class="sep" aria-hidden="true">|</span>'
					. '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M7.25 1.5h1.5v7.1l2.3-2.3 1.06 1.06L8 11.47 3.89 7.36 4.95 6.3l2.3 2.3V1.5ZM2.5 12.5h11V14h-11v-1.5Z"/></svg>'
					. 'Downloads: ' . (int) $downloads
					. '</div>';
			} catch (\Throwable $e) {
				error_log('JCRS Article Information plugin (statistics): ' . $e->getMessage());
			}

			if (trim(strip_tags($abstract)) !== '') {
				$keywordsHtml = '';
				$keywords = array_filter(array_map('trim', $keywords), 'strlen');
				if ($keywords) {
					$keywordsHtml = '<p class="jcrs-kw"><b>Keywords:</b> '
						. htmlspecialchars(implode(', ', $keywords), ENT_QUOTES, 'UTF-8') . '</p>';
				}
				$html .= '<details class="jcrs-abstract"><summary>Abstract</summary>'
					. '<div' . $lang . '>' . PKPString::stripUnsafeHtml($abstract) . $keywordsHtml . '</div>'
					. '</details>';
			}

			$output .= $html;
		} catch (\Throwable $e) {
			error_log('JCRS Article Information plugin: ' . $e->getMessage());
		}
		return false;
	}

	/**
	 * All-time abstract views and file downloads for a submission.
	 *
	 * @return array [views, downloads]
	 */
	private function getCounts($submissionId) {
		if (isset($this->countsCache[$submissionId])) {
			return $this->countsCache[$submissionId];
		}
		$views = $downloads = 0;
		import('classes.statistics.StatisticsHelper');
		$metricsDao = DAORegistry::getDAO('MetricsDAO');
		$rows = $metricsDao->getMetrics(
			OJS_METRIC_TYPE_COUNTER,
			[STATISTICS_DIMENSION_ASSOC_TYPE],
			[STATISTICS_DIMENSION_SUBMISSION_ID => $submissionId]
		);
		foreach ((array) $rows as $row) {
			$type = (int) $row[STATISTICS_DIMENSION_ASSOC_TYPE];
			$metric = (int) $row[STATISTICS_METRIC];
			if ($type === ASSOC_TYPE_SUBMISSION) {
				$views += $metric;
			} elseif ($type === ASSOC_TYPE_SUBMISSION_FILE) {
				$downloads += $metric;
			}
		}
		return $this->countsCache[$submissionId] = [$views, $downloads];
	}
}
